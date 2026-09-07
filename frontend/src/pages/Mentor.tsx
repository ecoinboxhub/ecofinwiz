import { useState, useRef, useEffect } from "react";
import { Send, Briefcase, RefreshCw } from "lucide-react";
import VoiceButton from "../components/VoiceButton";
import { useLanguage } from "../context/LanguageContext";
import { useTranslations } from "../i18n/useTranslations";
import { useChatStream } from "../hooks/useChatStream";

export default function Mentor() {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const { language } = useLanguage();
  const { t } = useTranslations();

  const { messages, sendMessage, loading, streamingContent, resetConversation } = useChatStream({
    endpoint: "/ai/mentor/chat",
    language,
  });

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingContent]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const text = input;
    setInput("");
    await sendMessage(text);
  };

  const newChat = () => {
    resetConversation();
  };

  const allMessages = streamingContent
    ? [...messages, { id: "streaming", role: "assistant" as const, content: streamingContent, timestamp: "" }]
    : messages;

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-lg mx-auto">
      <div className="px-4 py-3 flex items-center justify-between border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center">
            <Briefcase className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-gray-800 text-sm">{t("mentor.name")}</h1>
            <p className="text-xs text-gray-400">{t("mentor.role")}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{language.nativeName}</span>
          <button onClick={newChat} className="p-2 hover:bg-gray-100 rounded-xl transition-colors" title={t("advisor.newConversation")}>
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4" role="log" aria-live="polite">
        {messages.length === 0 && !loading && !streamingContent && (
          <div className="text-center py-10">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center mx-auto mb-4">
              <Briefcase className="w-8 h-8 text-white" />
            </div>
            <h2 className="font-semibold text-gray-700 mb-2">{t("mentor.welcomeTitle")}</h2>
            <p className="text-sm text-gray-400 max-w-xs mx-auto">{t("mentor.welcomeDesc")}</p>
            <div className="flex flex-wrap gap-2 justify-center mt-4">
              {[t("mentor.question1"), t("mentor.question2"), t("mentor.question3"), t("mentor.question4")].map((q) => (
                <button key={q} onClick={() => setInput(q)} className="text-xs bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-full text-gray-600 hover:bg-gold-50 hover:border-gold-200 transition-colors">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {allMessages.map((m) => (
          <div key={m.id} className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
            {m.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center flex-shrink-0">
                <Briefcase className="w-4 h-4 text-white" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${m.role === "user" ? "bg-gold-500 text-white rounded-br-lg" : "bg-gray-100 text-gray-700 rounded-bl-lg"}`}>
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.role === "assistant" && m.id !== "streaming" && (
                <div className="mt-2 flex justify-end">
                  <VoiceButton speakText={m.content} size="sm" language={language.code} />
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && !streamingContent && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center flex-shrink-0">
              <Briefcase className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-100 rounded-2xl rounded-bl-lg px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="px-4 py-3 border-t border-gray-100">
        <div className="flex gap-2 items-end">
          <VoiceButton onTranscript={(text) => setInput(prev => prev ? prev + " " + text : text)} size="md" language={language.code} />
          <input
            className="input-field flex-1"
            placeholder={t("mentor.placeholder")}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
          />
          <button onClick={handleSend} disabled={loading || !input.trim()} className="btn-primary !p-3 !rounded-xl">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
