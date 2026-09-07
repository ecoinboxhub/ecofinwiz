import { useState, useEffect } from "react";
import { MessageSquare, Pin, Lock, CheckCircle, Plus, ThumbsUp } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function Forum() {
  const { t } = useTranslations();
  const [topics, setTopics] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  useEffect(() => {
    client.get("/forum/topics").then(({ data }) => setTopics(Array.isArray(data) ? data : [])).catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post("/forum/topics", { title, content });
      setShowForm(false);
      setTitle("");
      setContent("");
      client.get("/forum/topics").then(({ data }) => setTopics(Array.isArray(data) ? data : []));
    } catch {}
  };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("forum.title")}</h1>
          <p className="text-sm text-gray-400">{t("forum.subtitle")}</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary !p-3 !rounded-xl"><Plus className="w-5 h-5" /></button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-3">
          <h3 className="font-semibold text-gray-800">{t("forum.newTopic")}</h3>
          <input className="input-field" placeholder={t("forum.titlePlaceholder")} value={title} onChange={e => setTitle(e.target.value)} required />
          <textarea className="input-field min-h-[100px]" placeholder={t("forum.contentPlaceholder")} value={content} onChange={e => setContent(e.target.value)} required />
          <div className="flex gap-2">
            <button type="submit" className="btn-primary flex-1">{t("forum.post")}</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">{t("common.cancel")}</button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {topics.length === 0 ? (
          <p className="text-center text-gray-400 text-sm py-8">{t("forum.empty")}</p>
        ) : topics.map((topic: any) => (
          <div key={topic.id} className="card !p-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center flex-shrink-0">
                <MessageSquare className="w-5 h-5 text-rose-500" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  {topic.is_pinned && <Pin className="w-3.5 h-3.5 text-sky-500" />}
                  {topic.is_locked && <Lock className="w-3.5 h-3.5 text-gray-400" />}
                  {topic.has_solution && <CheckCircle className="w-3.5 h-3.5 text-green-500" />}
                  <h3 className="font-medium text-gray-800 text-sm">{topic.title}</h3>
                </div>
                <p className="text-xs text-gray-400 mt-1 line-clamp-1">{topic.content?.slice(0, 100)}</p>
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                  <span>{topic.author_name || t("forum.anonymous")}</span>
                  <span className="flex items-center gap-1"><ThumbsUp className="w-3 h-3" />{topic.likes || 0}</span>
                  <span className="flex items-center gap-1"><MessageSquare className="w-3 h-3" />{topic.reply_count || 0}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <ChatWidget
        endpoint="/ai/advisor/chat"
        personaName="Kemi"
        personaRole="AI Financial Advisor"
        accent="from-sky-400 to-sky-600"
        iconBg="bg-gradient-to-r from-sky-500 to-sky-600"
        placeholder="Ask Kemi a question..."
        prompts={["I need financial advice", "Explain how to budget", "What should I ask the community?"]}
      />
    </div>
  );
}
