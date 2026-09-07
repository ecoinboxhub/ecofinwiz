"""
Multi-step autonomous agentic planning for AI assistants.

Enables the LLM to chain multiple tool calls in a single conversation turn,
auto-executing read tools and batching write tools for confirmation.
"""

import json
import re
from typing import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.modules.ai.providers import LLMProvider
from app.shared.logger import get_logger

logger = get_logger(__name__)

TOOL_PATTERN = re.compile(r"---TOOL:\s*(\w+)\s*(\{.*?\})---", re.DOTALL)

AUTO_TOOLS = {
    "get_budgets",
    "get_savings_goals",
    "get_invoices",
    "get_tasks",
    "get_spending_summary",
}

WRITE_TOOLS = {
    "create_budget",
    "record_transaction",
    "create_savings_goal",
    "create_invoice",
    "create_task",
    "generate_business_plan",
    "update_invoice",
    "delete_invoice",
    "mark_invoice_paid",
    "update_task",
    "delete_task",
}

ALL_TOOLS = AUTO_TOOLS | WRITE_TOOLS


class AgenticPlanner:
    """Manages multi-step autonomous tool execution with result feedback."""

    MAX_ITERATIONS = 5

    def __init__(
        self,
        db: AsyncSession,
        provider: LLMProvider,
        user: User,
        execute_tool_fn: Callable,
    ):
        self.db = db
        self.provider = provider
        self.user = user
        self._execute_tool = execute_tool_fn
        self.all_tool_results: list[dict] = []
        self.iterations = 0
        self.final_response = ""

    @staticmethod
    def parse_tool_calls(text: str) -> list[dict]:
        matches = list(TOOL_PATTERN.finditer(text))
        calls = []
        for m in matches:
            try:
                args = json.loads(m.group(2))
            except json.JSONDecodeError:
                continue
            calls.append({
                "name": m.group(1),
                "args": args,
                "start": m.start(),
                "end": m.end(),
            })
        return calls

    @staticmethod
    def strip_tool_blocks(text: str, calls: list[dict]) -> str:
        parts = []
        cursor = 0
        for c in sorted(calls, key=lambda x: x["start"]):
            parts.append(text[cursor:c["start"]])
            cursor = c["end"]
        parts.append(text[cursor:])
        return "".join(parts)

    async def run_streaming(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """Run the agentic loop yielding JSON-encoded SSE events."""
        while self.iterations < self.MAX_ITERATIONS:
            self.iterations += 1
            yield json.dumps({"event": "plan_iteration", "iteration": self.iterations})

            iteration_tokens = ""
            async for token in self.provider.chat_stream(messages):
                iteration_tokens += token
                yield json.dumps({"event": "token", "token": token})

            self.final_response += iteration_tokens
            tool_calls = self.parse_tool_calls(iteration_tokens)

            if not tool_calls:
                break

            auto_calls = [c for c in tool_calls if c["name"] in AUTO_TOOLS]
            write_calls = [c for c in tool_calls if c["name"] in WRITE_TOOLS]

            for tc in auto_calls:
                try:
                    result = await self._execute_tool(tc["name"], tc["args"])
                    entry = {"tool": tc["name"], "status": result.get("status"), "result": result}
                    self.all_tool_results.append(entry)
                    yield json.dumps({"event": "tool_executed", "tool": tc["name"], "result": result})
                except Exception as e:
                    entry = {"tool": tc["name"], "status": "error", "error": str(e)}
                    self.all_tool_results.append(entry)
                    yield json.dumps({"event": "tool_executed", "tool": tc["name"], "error": str(e)})

            if write_calls:
                pending = [{"tool": c["name"], "args": c["args"]} for c in write_calls]
                yield json.dumps({"event": "tools_pending", "tools": pending})

                for tc in write_calls:
                    try:
                        result = await self._execute_tool(tc["name"], tc["args"])
                        entry = {"tool": tc["name"], "status": result.get("status"), "result": result}
                        self.all_tool_results.append(entry)
                        yield json.dumps({"event": "tool_executed", "tool": tc["name"], "result": result})
                    except Exception as e:
                        entry = {"tool": tc["name"], "status": "error", "error": str(e)}
                        self.all_tool_results.append(entry)
                        yield json.dumps({"event": "tool_executed", "tool": tc["name"], "error": str(e)})

            yield json.dumps({"event": "tool_results", "results": list(self.all_tool_results)})

            clean_text = self.strip_tool_blocks(iteration_tokens, tool_calls)
            messages.append({"role": "assistant", "content": clean_text})

            recent = self.all_tool_results[-len(tool_calls):]
            result_summary = "; ".join(
                f"{r['tool']}: {r.get('result', {}).get('message', r.get('status', 'done'))}"
                for r in recent
            )
            messages.append({
                "role": "user",
                "content": f"Tool results: {result_summary}. Continue with the next step or respond naturally if done."
            })

        yield json.dumps({
            "event": "plan_complete",
            "iterations": self.iterations,
            "tool_count": len(self.all_tool_results),
        })

    async def run(self, messages: list[dict]) -> dict:
        """Non-streaming agentic loop. Returns final result dict."""
        while self.iterations < self.MAX_ITERATIONS:
            self.iterations += 1

            response = await self.provider.chat(messages)
            self.final_response += response
            tool_calls = self.parse_tool_calls(response)

            if not tool_calls:
                break

            auto_calls = [c for c in tool_calls if c["name"] in AUTO_TOOLS]
            write_calls = [c for c in tool_calls if c["name"] in WRITE_TOOLS]

            for tc in auto_calls + write_calls:
                try:
                    result = await self._execute_tool(tc["name"], tc["args"])
                    self.all_tool_results.append({
                        "tool": tc["name"],
                        "status": result.get("status"),
                        "result": result,
                    })
                except Exception as e:
                    self.all_tool_results.append({
                        "tool": tc["name"],
                        "status": "error",
                        "error": str(e),
                    })

            clean_text = self.strip_tool_blocks(response, tool_calls)
            messages.append({"role": "assistant", "content": clean_text})

            recent = self.all_tool_results[-len(tool_calls):]
            result_summary = "; ".join(
                f"{r['tool']}: {r.get('result', {}).get('message', r.get('status', 'done'))}"
                for r in recent
            )
            messages.append({
                "role": "user",
                "content": f"Tool results: {result_summary}. Continue with the next step or respond naturally if done."
            })

        return {
            "final_response": self.final_response,
            "tool_results": self.all_tool_results,
            "iterations": self.iterations,
        }
