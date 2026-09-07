import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, RefreshCw, MessageCircle, X } from "lucide-react";
import VoiceButton from "./VoiceButton";
import { useLanguage } from "../context/LanguageContext";
import { useTranslations } from "../i18n/useTranslations";
import { useChatStream } from "../hooks/useChatStream";

interface ChatWidgetProps {
  endpoint: string;
  personaName: string;
  personaRole: string;
  accent: string;
  iconBg: string;
  prompts: string[];
  placeholder?: string;
}

export default function ChatWidget({
  endpoint,
  personaName,
  personaRole,
  accent,
  iconBg,
  prompts,
  placeholder,
}: ChatWidgetProps) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const { language } = useLanguage();
  const { t } = useTranslations();

  const { messages, sendMessage, loading, streamingContent, resetConversation } = useChatStream({
    endpoint,
    language,
  });

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent, open]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const text = input;
    setInput("");
    await sendMessage(text);
  };

  const handleVoiceInput = (text: string) => {
    setInput(prev => prev ? prev + " " + text : text);
  };

  const allMessages = streamingContent
    ? [...messages, { id: "streaming", role: "assistant" as const, content: streamingContent, timestamp: "" }]
    : messages;

  return (
    <>
      {open && (
        <div className="fixed bottom-20 right-4 z-50 w-[22rem] max-w-[calc(100vw-2rem)] h-[28rem] max-h-[calc(100vh-6rem)] bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden">
          <div className={`px-4 py-3 flex items-center justify-between ${iconBg}`}>
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${accent} flex items-center justify-center`}>
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-white text-sm">{personaName}</h3>
                <p className="text-xs text-white/80">{personaRole}</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={resetConversation} className="p-1.5 rounded-lg hover:bg-white/20 text-white transition-colors" title={t("advisor.newConversation")}>
                <RefreshCw className="w-4 h-4" />
              </button>
              <button onClick={() => setOpen(false)} className="p-1.5 rounded-lg hover:bg-white/20 text-white transition-colors" title="Close">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4" role="log" aria-live="polite">
            {messages.length === 0 && !loading && !streamingContent && (
              <div className="text-center py-6">
                <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${accent} flex items-center justify-center mx-auto mb-3`}>
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 max-w-[14rem] mx-auto mb-3">{personaRole}</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {prompts.map((q) => (
                    <button key={q} onClick={() => setInput(q)} className="text-xs bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 px-3 py-1.5 rounded-full text-gray-600 dark:text-gray-300 hover:bg-sky-50 dark:hover:bg-sky-900/40 hover:border-sky-200 transition-colors">
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {allMessages.map((m) => (
              <div key={m.id} className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
                {m.role === "assistant" && (
                  <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${accent} flex items-center justify-center flex-shrink-0`}>
                    <Sparkles className="w-3.5 h-3.5 text-white" />
                  </div>
                )}
                <div className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm ${m.role === "user" ? "bg-sky-500 text-white rounded-br-lg" : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-bl-lg"}`}>
                  <div className="whitespace-pre-wrap">{m.content}</div>
                  {m.role === "assistant" && m.id !== "streaming" && (
                    <div className="mt-1.5 flex justify-end">
                      <VoiceButton speakText={m.content} size="sm" language={language.code} />
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && !streamingContent && (
              <div className="flex gap-3">
                <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${accent} flex items-center justify-center flex-shrink-0`}>
                  <Sparkles className="w-3.5 h-3.5 text-white" />
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-lg px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-300 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 bg-gray-300 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 bg-gray-300 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-700">
            <div className="flex gap-2 items-end">
              <VoiceButton onTranscript={handleVoiceInput} size="md" language={language.code} />
              <input
                className="input-field flex-1"
                placeholder={placeholder}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
              />
              <button onClick={handleSend} disabled={loading || !input.trim()} aria-label="Send message" className="btn-primary !p-3 !rounded-xl">
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-20 right-4 z-50 p-4 rounded-full bg-gradient-to-br from-sky-400 to-sky-600 text-white shadow-lg hover:shadow-xl transition-shadow"
          aria-label={`${personaName} chat`}
          title={`${personaName} - ${personaRole}`}
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}
    </>
  );
}