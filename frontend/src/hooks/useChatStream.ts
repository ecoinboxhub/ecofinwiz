import { useState, useCallback, useRef } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface UseChatStreamOptions {
  endpoint: string;
  language: { code: string; name: string };
  onError?: (msg: string) => void;
}

interface UseChatStreamReturn {
  messages: Message[];
  sendMessage: (text: string) => Promise<void>;
  loading: boolean;
  streamingContent: string;
  convId: string | null;
  resetConversation: () => void;
}

export function useChatStream({ endpoint, language, onError }: UseChatStreamOptions): UseChatStreamReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [convId, setConvId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setStreamingContent("");

    const currentInput = text + (language.code !== "en" ? ` [Respond in ${language.name}]` : "");

    try {
      const controller = new AbortController();
      abortRef.current = controller;

      const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8105/api/v1";
      const token = localStorage.getItem("access_token");

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: currentInput,
          conversation_id: convId,
        }),
        signal: controller.signal,
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No readable stream");

      const decoder = new TextDecoder();
      let buffer = "";
      let assistantContent = "";
      let finalConvId = convId;
      let streamEnded = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              const event = data.event;
              if (event === "started") {
                finalConvId = data.conversation_id;
                setConvId(data.conversation_id);
              } else if (event === "token") {
                assistantContent += data.token ?? "";
                setStreamingContent(assistantContent);
              } else if (event === "tool_executed" || event === "tool_results" || event === "plan_iteration" || event === "plan_complete") {
                // Agentic/tool events are not rendered as text; the stream continues.
              } else if (event === "done") {
                streamEnded = true;
                setMessages(prev => [
                  ...prev,
                  {
                    id: finalConvId || Date.now().toString(),
                    role: "assistant",
                    content: assistantContent,
                    timestamp: new Date().toISOString(),
                  },
                ]);
                setStreamingContent("");
              } else if (event === "error") {
                streamEnded = true;
                onError?.(data.message);
                setMessages(prev => [
                  ...prev,
                  {
                    id: Date.now().toString(),
                    role: "assistant",
                    content: data.message || "Service temporarily unavailable. Please try again.",
                    timestamp: new Date().toISOString(),
                  },
                ]);
                setStreamingContent("");
              }
            } catch {
              /* skip malformed JSON */
            }
          }
        }
      }

      if (!streamEnded) {
        if (assistantContent) {
          setMessages(prev => [
            ...prev,
            {
              id: finalConvId || Date.now().toString(),
              role: "assistant",
              content: assistantContent,
              timestamp: new Date().toISOString(),
            },
          ]);
          setStreamingContent("");
        }
      }
    } catch (err: any) {
      if (err.name === "AbortError") return;
      onError?.(err.message || "Request failed");
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  }, [endpoint, language.code, language.name, loading, convId, onError]);

  const resetConversation = useCallback(() => {
    setMessages([]);
    setConvId(null);
    setStreamingContent("");
  }, []);

  return { messages, sendMessage, loading, streamingContent, convId, resetConversation };
}
