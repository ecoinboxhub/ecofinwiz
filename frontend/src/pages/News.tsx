import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Newspaper, TrendingUp, Globe } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function News() {
  const { t } = useTranslations();
  const [news, setNews] = useState<any[]>([]);
  const [category, setCategory] = useState("all");

  useEffect(() => {
    const params: any = {};
    if (category !== "all") params.category = category;
    client.get("/news", { params }).then(({ data }) => setNews(Array.isArray(data) ? data : [])).catch(() => {});
  }, [category]);

  const categories = ["all", "financial", "business", "economy", "startups"];

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <h1 className="text-xl font-bold text-gray-800">{t("news.title")}</h1>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {categories.map(c => (
          <button key={c} onClick={() => setCategory(c)} className={`px-4 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${category === c ? "bg-orange-500 text-white" : "bg-gray-100 text-gray-500"}`}>
            {t("news." + c)}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {news.length === 0 ? (
          <div className="text-center py-10">
            <Globe className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{t("news.empty")}</p>
            <p className="text-xs text-gray-300 mt-1">News feed updates when articles are published</p>
          </div>
        ) : news.map((n: any) => (
          <Link key={n.id || n._id} to={`/news/${n.id || n._id}`} className="card !p-4 block hover:shadow-md transition-shadow">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center flex-shrink-0">
                <Newspaper className="w-5 h-5 text-orange-500" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-800 text-sm mb-1">{n.title}</h3>
                <p className="text-xs text-gray-400 line-clamp-2 mb-2">{n.summary || n.content?.slice(0, 120)}</p>
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  {n.source && <span className="font-medium text-gray-500">{n.source}</span>}
                  {n.category && <span className="badge-orange">{n.category}</span>}
                  {n.date && <span>{new Date(n.date).toLocaleDateString()}</span>}
                </div>
              </div>
            </div>
            {n.is_breaking && <div className="mt-2 bg-rose-50 text-rose-600 text-xs font-medium px-2 py-0.5 rounded-full inline-flex items-center gap-1"><TrendingUp className="w-3 h-3" />{t("news.breaking")}</div>}
          </Link>
        ))}
      </div>

      <ChatWidget
        endpoint="/ai/investment/chat"
        personaName="Musa"
        personaRole="AI Investment Advisor"
        accent="from-emerald-400 to-emerald-600"
        iconBg="bg-gradient-to-r from-emerald-500 to-emerald-600"
        placeholder="Ask Musa about market news..."
        prompts={["What does this rate hike mean for me?", "Explain today's market movers", "How should I react to this news?"]}
      />
    </div>
  );
}
