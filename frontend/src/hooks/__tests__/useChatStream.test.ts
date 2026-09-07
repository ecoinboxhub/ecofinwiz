import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { useChatStream } from "../useChatStream";

const encoder = new TextEncoder();

function sseResponse(chunks: string[], delayMs = 0): Response {
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
        if (delayMs > 0) await new Promise((r) => setTimeout(r, delayMs));
      }
      controller.close();
    },
  });
  return new Response(stream, { status: 200, headers: { "Content-Type": "text/event-stream" } });
}

function mockFetch(chunks: string[], delayMs = 0) {
  const fn = vi.fn().mockResolvedValue(sseResponse(chunks, delayMs));
  vi.stubGlobal("fetch", fn);
  return fn;
}

const en = { code: "en", name: "English" };

beforeEach(() => localStorage.clear());
afterEach(() => vi.unstubAllGlobals());

describe("useChatStream", () => {
  it("appends the user message and streams the assistant reply on done", async () => {
    const fetchMock = mockFetch([
      'data: {"event": "started", "conversation_id": "conv-1"}\n\n',
      'data: {"event": "token", "token": "Hello"}\n\n',
      'data: {"event": "token", "token": " world"}\n\n',
      'data: {"event": "done", "message_id": "m-1", "conversation_id": "conv-1"}\n\n',
    ]);

    const { result } = renderHook(() => useChatStream({ endpoint: "/ai/advisor/chat", language: en }));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/ai/advisor/chat"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ message: "Hi", conversation_id: null }),
      })
    );
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0]).toMatchObject({ role: "user", content: "Hi" });
    expect(result.current.messages[1]).toMatchObject({ role: "assistant", content: "Hello world" });
    expect(result.current.convId).toBe("conv-1");
    expect(result.current.loading).toBe(false);
    expect(result.current.streamingContent).toBe("");
  });

  it("does not double-append the assistant message when done is received", async () => {
    mockFetch([
      'data: {"event": "token", "token": "Only once"}\n\n',
      'data: {"event": "done", "message_id": "m-1"}\n\n',
    ]);

    const { result } = renderHook(() => useChatStream({ endpoint: "/ai/advisor/chat", language: en }));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].content).toBe("Only once");
  });

  it("appends an error message on the error event", async () => {
    mockFetch(['data: {"event": "error", "message": "Rate limit reached"}\n\n']);

    const onError = vi.fn();
    const { result } = renderHook(() => useChatStream({ endpoint: "/ai/advisor/chat", language: en, onError }));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });

    expect(onError).toHaveBeenCalledWith("Rate limit reached");
    expect(result.current.messages[1]).toMatchObject({ role: "assistant", content: "Rate limit reached" });
  });

  it("appends accumulated tokens if the stream closes without done/error", async () => {
    mockFetch([
      'data: {"event": "started", "conversation_id": "conv-2"}\n\n',
      'data: {"event": "token", "token": "Partial reply"}\n\n',
    ]);

    const { result } = renderHook(() => useChatStream({ endpoint: "/ai/advisor/chat", language: en }));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].content).toBe("Partial reply");
  });

  it("appends a non-en language suffix to the request body", async () => {
    const fetchMock = mockFetch(['data: {"event": "done", "message_id": "m-1"}\n\n']);

    const { result } = renderHook(() =>
      useChatStream({ endpoint: "/ai/advisor/chat", language: { code: "yo", name: "Yoruba" } })
    );

    await act(async () => {
      await result.current.sendMessage("Bani");
    });

    const body = JSON.parse((fetchMock.mock.calls[0][1] as RequestInit).body as string);
    expect(body.message).toBe("Bani [Respond in Yoruba]");
  });

  it("shows streaming tokens live before the done event", async () => {
    mockFetch(
      [
        'data: {"event": "token", "token": "Hello"}\n\n',
        'data: {"event": "token", "token": " world"}\n\n',
        'data: {"event": "done", "message_id": "m-1"}\n\n',
      ],
      150
    );

    const { result } = renderHook(() => useChatStream({ endpoint: "/ai/advisor/chat", language: en }));

    let sendPromise: Promise<void>;
    act(() => {
      sendPromise = result.current.sendMessage("Hi");
    });

    await act(async () => {
      await new Promise((r) => setTimeout(r, 100));
    });
    expect(result.current.streamingContent).toBe("Hello");

    await act(async () => {
      await sendPromise;
    });
    expect(result.current.streamingContent).toBe("");
    expect(result.current.messages[1].content).toBe("Hello world");
  });

  it("sends the existing conversation_id on follow-up messages", async () => {
    const fetchMock = mockFetch([
      'data: {"event": "started", "conversation_id": "conv-1"}\n\n',
      'data: {"event": "done", "message_id": "m-1"}\n\n',
    ]);

    const { result } = renderHook(() => useChatStream({ endpoint: "/ai/advisor/chat", language: en }));

    await act(async () => {
      await result.current.sendMessage("First");
    });

    await act(async () => {
      await result.current.sendMessage("Second");
    });

    const bodies = fetchMock.mock.calls.map(([, init]) => JSON.parse((init as RequestInit).body as string));
    expect(bodies[1].conversation_id).toBe("conv-1");
  });

  it("resetConversation clears messages, convId and streaming content", async () => {
    mockFetch([
      'data: {"event": "started", "conversation_id": "conv-1"}\n\n',
      'data: {"event": "done", "message_id": "m-1"}\n\n',
    ]);

    const { result } = renderHook(() => useChatStream({ endpoint: "/ai/advisor/chat", language: en }));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });
    expect(result.current.messages).toHaveLength(2);

    act(() => result.current.resetConversation());
    expect(result.current.messages).toHaveLength(0);
    expect(result.current.convId).toBeNull();
    expect(result.current.streamingContent).toBe("");
  });
});