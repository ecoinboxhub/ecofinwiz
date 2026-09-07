import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ChatWidget from "../ChatWidget";
import { LanguageProvider } from "../../context/LanguageContext";

const encoder = new TextEncoder();

function sseResponse(chunks: string[]): Response {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
  return new Response(stream, { status: 200, headers: { "Content-Type": "text/event-stream" } });
}

function mockFetch(chunks: string[]) {
  const fn = vi.fn().mockResolvedValue(sseResponse(chunks));
  vi.stubGlobal("fetch", fn);
  return fn;
}

const props = {
  endpoint: "/ai/advisor/chat",
  personaName: "Kemi",
  personaRole: "AI Financial Advisor",
  accent: "from-sky-400 to-sky-600",
  iconBg: "bg-gradient-to-r from-sky-500 to-sky-600",
  prompts: ["Create a budget", "Help me save"],
  placeholder: "Ask Kemi...",
};

function renderChat() {
  return render(
    <LanguageProvider>
      <ChatWidget {...props} />
    </LanguageProvider>
  );
}

beforeEach(() => localStorage.clear());
afterEach(() => vi.unstubAllGlobals());

describe("ChatWidget", () => {
  it("renders a closed toggle button, then opens the panel showing persona and prompts", () => {
    renderChat();

    const toggle = screen.getByRole("button", { name: "Kemi chat" });
    expect(toggle).toBeInTheDocument();
    expect(screen.queryByText("AI Financial Advisor")).not.toBeInTheDocument();

    fireEvent.click(toggle);

    expect(screen.getByText("Kemi")).toBeInTheDocument();
    expect(screen.getAllByText("AI Financial Advisor").length).toBeGreaterThan(0);
    expect(screen.getByText("Create a budget")).toBeInTheDocument();
    expect(screen.getByText("Help me save")).toBeInTheDocument();
  });

  it("fills the input when a suggested prompt is clicked", () => {
    renderChat();
    fireEvent.click(screen.getByRole("button", { name: "Kemi chat" }));
    fireEvent.click(screen.getByText("Create a budget"));

    const input = screen.getByPlaceholderText("Ask Kemi...") as HTMLInputElement;
    expect(input.value).toBe("Create a budget");
  });

  it("streams a user message and assistant reply into the panel", async () => {
    mockFetch([
      'data: {"event": "started", "conversation_id": "conv-1"}\n\n',
      'data: {"event": "token", "token": "Try a 50-30-20 split"}\n\n',
      'data: {"event": "done", "message_id": "m-1"}\n\n',
    ]);

    renderChat();
    fireEvent.click(screen.getByRole("button", { name: "Kemi chat" }));

    const input = screen.getByPlaceholderText("Ask Kemi...");
    fireEvent.change(input, { target: { value: "Help me budget" } });
    fireEvent.click(screen.getByRole("button", { name: /Send/ }));

    await waitFor(() => {
      expect(screen.getByText("Help me budget")).toBeInTheDocument();
    });
    expect(await screen.findByText("Try a 50-30-20 split")).toBeInTheDocument();
    expect(screen.queryByText("Ask Kemi...")).not.toBeInTheDocument();
  });

  it("surfaces an error event message in the panel", async () => {
    mockFetch(['data: {"event": "error", "message": "Rate limit reached"}\n\n']);

    renderChat();
    fireEvent.click(screen.getByRole("button", { name: "Kemi chat" }));

    const input = screen.getByPlaceholderText("Ask Kemi...");
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.click(screen.getByRole("button", { name: /Send/ }));

    expect(await screen.findByText("Rate limit reached")).toBeInTheDocument();
  });

  it("reset clears the conversation", async () => {
    mockFetch([
      'data: {"event": "started", "conversation_id": "conv-1"}\n\n',
      'data: {"event": "done", "message_id": "m-1"}\n\n',
    ]);

    renderChat();
    fireEvent.click(screen.getByRole("button", { name: "Kemi chat" }));

    const input = screen.getByPlaceholderText("Ask Kemi...");
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.click(screen.getByRole("button", { name: /Send/ }));

    await waitFor(() => {
      expect(screen.getByText("Hello")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTitle("New conversation"));
    expect(screen.queryByText("Hello")).not.toBeInTheDocument();
    expect(screen.getByText("Create a budget")).toBeInTheDocument();
  });
});