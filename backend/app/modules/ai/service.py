"""
AI service orchestrator.

Coordinates: guardrails → context + RAG → prompt assembly → LLM
→ action dispatch → output guardrails → response storage → feedback.
"""

import json
import re
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import NotFoundException
from app.models import User, AIConversation, AIMessage
from app.modules.ai.context import ContextAssembler
from app.modules.ai.guardrails import check_input_safety, check_output_safety
from app.modules.ai.providers import LLMProvider, get_provider
from app.modules.ai.agent import AgenticPlanner
from app.modules.ai.prompts import FINANCIAL_ADVISOR_SYSTEM, BUSINESS_MENTOR_SYSTEM, INVESTMENT_ADVISOR_SYSTEM
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

SYSTEM_PROMPTS = {
    "advisor": FINANCIAL_ADVISOR_SYSTEM,
    "mentor": BUSINESS_MENTOR_SYSTEM,
    "investment": INVESTMENT_ADVISOR_SYSTEM,
}

TOOL_PATTERN = re.compile(r"---TOOL:\s*(\w+)\s*(\{.*?\})---", re.DOTALL)


class AIService:
    def __init__(self, db: AsyncSession, provider_name: str = "fallback"):
        self.db = db
        self.provider: LLMProvider = get_provider(provider_name)
        self.context = ContextAssembler(db)

    async def _find_or_create_conv(
        self, user: User, message: str, conversation_type: str, conversation_id: Optional[str]
    ) -> AIConversation:
        if conversation_id:
            result = await self.db.execute(
                select(AIConversation).where(
                    AIConversation.id == uuid.UUID(conversation_id),
                    AIConversation.user_id == user.id,
                )
            )
            conv = result.scalar_one_or_none()
            if conv:
                return conv
        title = message[:80] + ("..." if len(message) > 80 else "")
        conv = AIConversation(
            user_id=user.id,
            type=conversation_type,
            title=title,
        )
        self.db.add(conv)
        await self.db.flush()
        return conv

    async def _execute_tool(self, tool_name: str, args: dict, user: User) -> dict:
        from datetime import date, timedelta
        from app.modules.finance.service import FinanceService
        from app.modules.business.service import (
            create_invoice as biz_create_invoice,
            update_invoice as biz_update_invoice,
            delete_invoice as biz_delete_invoice,
            mark_invoice_paid as biz_mark_invoice_paid,
            create_task as biz_create_task,
            update_task as biz_update_task,
            delete_task as biz_delete_task,
            list_invoices as biz_list_invoices,
            list_tasks as biz_list_tasks,
            generate_business_plan as biz_gen_plan,
        )
        from app.modules.business.schemas import InvoiceCreate, InvoiceItem, InvoiceUpdate, TaskCreate, TaskUpdate, BusinessPlanGenerate

        user_id = user.id

        if tool_name == "create_budget":
            svc = FinanceService(self.db)
            data = {
                "category": args["category"],
                "budget_amount": float(args["budget_amount"]),
                "period": args.get("period", "monthly"),
            }
            budget = await svc.create_budget(user_id=user_id, data=data)
            return {"status": "ok", "message": f"Budget created for {args['category']}: ₦{args['budget_amount']}", "budget_id": str(budget.id)}

        if tool_name == "record_transaction":
            svc = FinanceService(self.db)
            txn = await svc.create_transaction(
                user_id=user_id,
                data={
                    "amount": float(args["amount"]),
                    "category": args["category"],
                    "description": args.get("description", ""),
                    "type": args["transaction_type"],
                },
            )
            return {"status": "ok", "message": f"{args['transaction_type'].title()} of ₦{args['amount']} recorded for {args['category']}", "transaction_id": str(txn.id)}

        if tool_name == "get_spending_summary":
            today = date.today()
            month_start = today.replace(day=1)
            svc = FinanceService(self.db)
            summary = await svc.get_spending_summary(user_id=user_id, start_date=month_start)
            return {"status": "ok", "summary": summary}

        if tool_name == "create_savings_goal":
            svc = FinanceService(self.db)
            goal = await svc.create_savings_goal(
                user_id=user_id,
                data={"name": args["name"], "target_amount": float(args["target_amount"])},
            )
            return {"status": "ok", "message": f"Savings goal '{args['name']}' created for ₦{args['target_amount']}", "goal_id": str(goal.id)}

        if tool_name == "get_budgets":
            svc = FinanceService(self.db)
            budgets = await svc.list_budgets(user_id=user_id)
            budget_names = [(b.category, float(b.budget_amount)) for b in budgets]
            return {"status": "ok", "budgets": budget_names}

        if tool_name == "get_savings_goals":
            svc = FinanceService(self.db)
            goals = await svc.list_savings_goals(user_id=user_id)
            goal_names = [(g.name, float(g.target_amount), float(g.current_amount or 0)) for g in goals]
            return {"status": "ok", "goals": goal_names}

        if tool_name == "create_invoice":
            item = InvoiceItem(
                description=args.get("description", "Services"),
                quantity=1,
                unit_price=float(args["amount"]),
            )
            data = InvoiceCreate(
                client_name=args["client_name"],
                items=[item],
            )
            invoice = await biz_create_invoice(data=data, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Invoice #{invoice.invoice_number} created for {args['client_name']}: ₦{args['amount']}", "invoice_id": str(invoice.id)}

        if tool_name == "create_task":
            due = None
            if args.get("due_date"):
                from datetime import datetime
                try:
                    due = datetime.strptime(args["due_date"], "%Y-%m-%d")
                except ValueError:
                    due = None
            data = TaskCreate(
                title=args["title"],
                description=args.get("description", ""),
                priority=args.get("priority", "medium"),
                due_date=due,
            )
            task = await biz_create_task(data=data, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Task '{args['title']}' created", "task_id": str(task.id)}

        if tool_name == "get_invoices":
            invoices = await biz_list_invoices(user_id=user_id, db=self.db, status=args.get("status"))
            inv_list = [(i.invoice_number, i.client_name, float(i.total_amount), i.status) for i in invoices]
            return {"status": "ok", "invoices": inv_list}

        if tool_name == "get_tasks":
            tasks = await biz_list_tasks(user_id=user_id, db=self.db, status=args.get("status"))
            task_list = [(t.title, t.priority, t.status) for t in tasks]
            return {"status": "ok", "tasks": task_list}

        if tool_name == "generate_business_plan":
            data = BusinessPlanGenerate(
                business_name=args.get("business_name", "My Business"),
                industry=args.get("industry", "General"),
                description=args.get("description", ""),
                target_market=args.get("target_market", ""),
            )
            plan = await biz_gen_plan(data=data, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Business plan generated for {data.business_name}", "plan": plan}

        if tool_name == "update_invoice":
            inv_id = uuid.UUID(args["invoice_id"])
            data = InvoiceUpdate(
                client_name=args.get("client_name"),
                notes=args.get("notes"),
                due_date=datetime.fromisoformat(args["due_date"]) if args.get("due_date") else None,
            )
            inv = await biz_update_invoice(invoice_id=inv_id, data=data, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Invoice #{inv.invoice_number} updated", "invoice_id": str(inv.id)}

        if tool_name == "delete_invoice":
            inv_id = uuid.UUID(args["invoice_id"])
            await biz_delete_invoice(invoice_id=inv_id, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Invoice deleted"}

        if tool_name == "mark_invoice_paid":
            inv_id = uuid.UUID(args["invoice_id"])
            inv = await biz_mark_invoice_paid(invoice_id=inv_id, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Invoice #{inv.invoice_number} marked as paid", "invoice_id": str(inv.id)}

        if tool_name == "update_task":
            task_id = uuid.UUID(args["task_id"])
            data = TaskUpdate(
                title=args.get("title"),
                description=args.get("description"),
                status=args.get("status"),
                priority=args.get("priority"),
                due_date=datetime.fromisoformat(args["due_date"]) if args.get("due_date") else None,
            )
            task = await biz_update_task(task_id=task_id, data=data, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Task '{task.title}' updated", "task_id": str(task.id)}

        if tool_name == "delete_task":
            task_id = uuid.UUID(args["task_id"])
            await biz_delete_task(task_id=task_id, user_id=user_id, db=self.db)
            return {"status": "ok", "message": f"Task deleted"}

        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    async def _process_tool_calls(self, text: str, user: User) -> tuple[str, list[dict]]:
        matches = list(TOOL_PATTERN.finditer(text))
        if not matches:
            return text, []
        results = []
        cursor = 0
        processed_parts = []
        for match in matches:
            tool_name = match.group(1)
            raw_args = match.group(2)
            processed_parts.append(text[cursor:match.start()])
            cursor = match.end()
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                results.append({"tool": tool_name, "status": "error", "error": "Invalid JSON arguments"})
                processed_parts.append(f"\n[Tool {tool_name} failed: invalid arguments]\n")
                continue
            try:
                result = await self._execute_tool(tool_name, args, user)
                results.append({"tool": tool_name, "status": result.get("status"), "result": result})
                msg = result.get("message", result.get("status", "done"))
                processed_parts.append(f"\n[✓ {msg}]\n")
            except Exception as e:
                results.append({"tool": tool_name, "status": "error", "error": str(e)})
                processed_parts.append(f"\n[✗ {tool_name} failed: {e}]\n")
        processed_parts.append(text[cursor:])
        return "".join(processed_parts), results

    async def _build_llm_messages(
        self, user: User, message: str, conversation_type: str, conv: AIConversation, with_rag: bool = True
    ) -> list[dict]:
        if with_rag:
            context = await self.context.assemble_with_rag(user, message, conversation_type, conv.id)
        else:
            context = await self.context.assemble(user, conversation_type, conv.id)

        history = await self.context.get_conversation_history(conv.id)
        system_prompt = SYSTEM_PROMPTS.get(conversation_type, FINANCIAL_ADVISOR_SYSTEM)
        full_system = f"{system_prompt}\n\n## Current User Context\n{context}"

        llm_messages = [{"role": "system", "content": full_system}]
        for msg in history:
            llm_messages.append(msg)
        llm_messages.append({"role": "user", "content": message})
        return llm_messages

    async def chat_stream(
        self,
        user: User,
        message: str,
        conversation_type: str = "advisor",
        conversation_id: Optional[str] = None,
        enable_agentic: bool = False,
    ) -> AsyncGenerator[str, None]:
        conv = await self._find_or_create_conv(user, message, conversation_type, conversation_id)

        guardrail = check_input_safety(message)
        sanitized_message = guardrail.sanitized_text or message

        user_msg = AIMessage(
            conversation_id=conv.id,
            role="user",
            content=sanitized_message,
            extra_data={"warnings": guardrail.reason} if guardrail.reason else None,
        )
        self.db.add(user_msg)
        await self.db.flush()

        yield json.dumps({"event": "started", "conversation_id": str(conv.id)})

        try:
            llm_messages = await self._build_llm_messages(user, sanitized_message, conversation_type, conv, with_rag=True)

            if enable_agentic:
                planner = AgenticPlanner(self.db, self.provider, user, self._execute_tool)
                async for event in planner.run_streaming(llm_messages):
                    yield event
                full_response = planner.final_response
                tool_results = planner.all_tool_results
            else:
                full_response = ""
                async for token in self.provider.chat_stream(llm_messages):
                    full_response += token
                    yield json.dumps({"event": "token", "token": token})

                processed_response, tool_results = await self._process_tool_calls(full_response, user)

                if tool_results:
                    yield json.dumps({"event": "tool_results", "results": tool_results})
                    llm_messages.append({"role": "assistant", "content": processed_response})
                    llm_messages.append({"role": "user", "content": "Continue with the result above. Respond naturally to the user."})
                    full_response = ""
                    async for token in self.provider.chat_stream(llm_messages):
                        full_response += token
                        yield json.dumps({"event": "token", "token": token})

            safety_check = check_output_safety(full_response)
            if not safety_check.passed:
                blocked_response = (
                    "I apologize, but my response was flagged by our safety filters. "
                    "Please rephrase your question or contact support if you believe this is an error."
                )
                assistant_msg = AIMessage(
                    conversation_id=conv.id,
                    role="assistant",
                    content=blocked_response,
                    extra_data={"blocked": True, "reason": safety_check.reason},
                )
                self.db.add(assistant_msg)
                await self.db.flush()
                yield json.dumps({"event": "done", "message_id": str(assistant_msg.id), "conversation_id": str(conv.id)})
                return

            assistant_msg = AIMessage(
                conversation_id=conv.id,
                role="assistant",
                content=full_response,
            )
            self.db.add(assistant_msg)
            await self.db.flush()

            yield json.dumps({"event": "done", "message_id": str(assistant_msg.id), "conversation_id": str(conv.id)})

        except Exception as e:
            logger.error(f"AI chat error: {e}", exc_info=True)
            yield json.dumps({"event": "error", "message": "Service temporarily unavailable. Please try again.", "conversation_id": str(conv.id)})

    # ── Non-streaming chat (for sync use) ──

    async def chat(
        self,
        user: User,
        message: str,
        conversation_type: str = "advisor",
        conversation_id: Optional[str] = None,
        enable_agentic: bool = False,
    ) -> dict:
        conv = await self._find_or_create_conv(user, message, conversation_type, conversation_id)

        guardrail = check_input_safety(message)
        sanitized_message = guardrail.sanitized_text or message

        user_msg = AIMessage(
            conversation_id=conv.id,
            role="user",
            content=sanitized_message,
            extra_data={"warnings": guardrail.reason} if guardrail.reason else None,
        )
        self.db.add(user_msg)
        await self.db.flush()

        llm_messages = await self._build_llm_messages(user, sanitized_message, conversation_type, conv, with_rag=True)

        if enable_agentic:
            planner = AgenticPlanner(self.db, self.provider, user, self._execute_tool)
            result = await planner.run(llm_messages)
            response = result["final_response"]
            tool_results = result["tool_results"]
        else:
            response = await self.provider.chat(llm_messages)

            processed_response, tool_results = await self._process_tool_calls(response, user)

            if tool_results:
                llm_messages.append({"role": "assistant", "content": processed_response})
                llm_messages.append({"role": "user", "content": "Continue with the result above. Respond naturally to the user."})
                response = await self.provider.chat(llm_messages)

        safety_check = check_output_safety(response)
        if not safety_check.passed:
            logger.warning(f"Output guardrail blocked response: {safety_check.reason}")
            logger.warning(f"Blocked response preview: {response[:200]}")
            response = (
                "I apologize, but my response was flagged by our safety filters. "
                "Please rephrase your question or contact support if you believe this is an error."
            )

        assistant_msg = AIMessage(
            conversation_id=conv.id,
            role="assistant",
            content=response,
        )
        self.db.add(assistant_msg)
        await self.db.flush()

        return {
            "response": response,
            "conversation_id": str(conv.id),
            "message_id": str(assistant_msg.id),
        }

    # ── Conversation management ──

    async def list_conversations(
        self, user_id: uuid.UUID, conv_type: str = "advisor", skip: int = 0, limit: int = 20
    ) -> tuple[list[AIConversation], int]:
        count_result = await self.db.execute(
            select(func.count(AIConversation.id)).where(
                AIConversation.user_id == user_id,
                AIConversation.type == conv_type,
            )
        )
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(AIConversation)
            .where(
                AIConversation.user_id == user_id,
                AIConversation.type == conv_type,
            )
            .order_by(AIConversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        conversations = list(result.scalars().all())

        for conv in conversations:
            msg_count = await self.db.execute(
                select(func.count(AIMessage.id)).where(
                    AIMessage.conversation_id == conv.id,
                    AIMessage.role != "system",
                )
            )
            conv.message_count = msg_count.scalar() or 0

        return conversations, total

    async def get_conversation(
        self, conv_id: uuid.UUID, user_id: uuid.UUID
    ) -> AIConversation:
        result = await self.db.execute(
            select(AIConversation).where(
                AIConversation.id == conv_id,
                AIConversation.user_id == user_id,
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            raise NotFoundException("Conversation")
        return conv

    async def get_conversation_messages(
        self, conv_id: uuid.UUID, user_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[AIMessage]:
        conv = await self.get_conversation(conv_id, user_id)
        result = await self.db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conv.id)
            .order_by(AIMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def archive_conversation(self, conv_id: uuid.UUID, user_id: uuid.UUID) -> AIConversation:
        conv = await self.get_conversation(conv_id, user_id)
        conv.is_archived = True
        await self.db.flush()
        return conv

    async def delete_conversation(self, conv_id: uuid.UUID, user_id: uuid.UUID) -> None:
        conv = await self.get_conversation(conv_id, user_id)
        await self.db.delete(conv)
        await self.db.flush()

    # ── Feedback / Rating ──

    async def rate_message(
        self, message_id: uuid.UUID, user_id: uuid.UUID, rating: int, feedback_text: Optional[str] = None
    ) -> AIMessage:
        result = await self.db.execute(
            select(AIMessage).where(
                AIMessage.id == message_id,
                AIMessage.role == "assistant",
            )
        )
        msg = result.scalar_one_or_none()
        if not msg:
            raise NotFoundException("Message")

        conv_result = await self.db.execute(
            select(AIConversation).where(
                AIConversation.id == msg.conversation_id,
                AIConversation.user_id == user_id,
            )
        )
        conv = conv_result.scalar_one_or_none()
        if not conv:
            raise NotFoundException("Conversation")

        msg.rating = rating
        if feedback_text:
            extra = msg.extra_data or {}
            extra["feedback"] = feedback_text
            msg.extra_data = extra

        await self.db.flush()
        return msg
