import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FileText, Search, BookOpen } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function Articles() {
  const { t } = useTranslations();
  const [articles, setArticles] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    client.get("/articles").then(({ data }) => setArticles(Array.isArray(data) ? data : [])).catch(() => {});
  }, []);

  const filtered = articles.filter((a: any) => a.title?.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <h1 className="text-xl font-bold text-gray-800">{t("articles.title")}</h1>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input className="input-field pl-10" placeholder={t("articles.searchPlaceholder")} value={search} onChange={e => setSearch(e.target.value)} />
      </div>
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-10">
            <BookOpen className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{search ? "No articles match your search" : t("articles.empty")}</p>
            {!search && <p className="text-xs text-gray-300 mt-1">Check back soon for new articles</p>}
          </div>
        ) : filtered.map((a: any) => (
          <Link key={a.id || a._id} to={`/articles/${a.id || a._id}`} className="card !p-4 hover:shadow-md transition-shadow cursor-pointer block">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-sky-50 flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-sky-500" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-800 text-sm mb-1">{a.title}</h3>
                <p className="text-xs text-gray-400 line-clamp-2">{a.summary || a.content?.slice(0, 120)}</p>
                <div className="flex items-center gap-2 mt-2">
                  {a.category && <span className="badge-sky">{a.category}</span>}
                  <span className="text-xs text-gray-400">{a.read_time || t("articles.readTime")}</span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      <ChatWidget
        endpoint="/ai/investment/chat"
        personaName="Musa"
        personaRole="AI Investment Advisor"
        accent="from-emerald-400 to-emerald-600"
        iconBg="bg-gradient-to-r from-emerald-500 to-emerald-600"
        placeholder="Ask Musa about investing..."
        prompts={["Explain diversification", "What are the best investments for beginners?", "How does the NSE work?"]}
      />
    </div>
  );
}
