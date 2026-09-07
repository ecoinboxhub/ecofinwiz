import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { MessageSquare, Heart, PenTool } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function Blog() {
  const { t } = useTranslations();
  const [posts, setPosts] = useState<any[]>([]);

  useEffect(() => {
    client.get("/blog").then(({ data }) => setPosts(Array.isArray(data) ? data : [])).catch(() => {});
  }, []);

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <h1 className="text-xl font-bold text-gray-800">{t("blog.title")}</h1>
      <div className="space-y-3">
        {posts.length === 0 ? (
          <div className="text-center py-10">
            <PenTool className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{t("blog.empty")}</p>
            <p className="text-xs text-gray-300 mt-1">Stay tuned for upcoming posts</p>
          </div>
        ) : posts.map((p: any) => (
          <Link key={p.id || p._id} to={`/blog/${p.id || p._id}`} className="card !p-4 block hover:shadow-md transition-shadow">
            <h3 className="font-medium text-gray-800 mb-1">{p.title}</h3>
            <p className="text-sm text-gray-500 mb-3 line-clamp-2">{p.content?.slice(0, 150)}</p>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{p.author || t("blog.anonymous")}</span>
              <span className="flex items-center gap-1"><Heart className="w-3 h-3" />{p.likes || 0}</span>
              <span className="flex items-center gap-1"><MessageSquare className="w-3 h-3" />{p.comment_count || 0}</span>
            </div>
          </Link>
        ))}
      </div>

      <ChatWidget
        endpoint="/ai/advisor/chat"
        personaName="Kemi"
        personaRole="AI Financial Advisor"
        accent="from-sky-400 to-sky-600"
        iconBg="bg-gradient-to-r from-sky-500 to-sky-600"
        placeholder="Ask Kemi about this topic..."
        prompts={["What should I read next?", "Explain the latest fintech trends", "Give me financial advice"]}
      />
    </div>
  );
}
