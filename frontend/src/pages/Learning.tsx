import { useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, Newspaper, MessageSquare, PenTool } from "lucide-react";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

const CATEGORIES = ["all", "personalFinance", "investing", "business", "tax", "insurance", "career"] as const;

const TOPICS = [
  { key: "budgetingBasics", desc: "budgetingDesc", icon: "💰", category: "personalFinance", lessons: 5 },
  { key: "savingStrategies", desc: "savingDesc", icon: "🏦", category: "personalFinance", lessons: 4 },
  { key: "investmentFundamentals", desc: "investmentDesc", icon: "📈", category: "investing", lessons: 6 },
  { key: "debtManagement", desc: "debtDesc", icon: "💳", category: "personalFinance", lessons: 4 },
  { key: "taxBasics", desc: "taxDesc", icon: "🧾", category: "tax", lessons: 5 },
  { key: "insuranceGuide", desc: "insuranceDesc", icon: "🛡️", category: "insurance", lessons: 4 },
  { key: "startingBusiness", desc: "startingDesc", icon: "🚀", category: "business", lessons: 7 },
  { key: "digitalMarketing", desc: "digitalDesc", icon: "📱", category: "business", lessons: 5 },
  { key: "pricingProfit", desc: "pricingDesc", icon: "💲", category: "business", lessons: 4 },
  { key: "realEstate", desc: "realEstateDesc", icon: "🏠", category: "investing", lessons: 5 },
  { key: "cryptoAssets", desc: "cryptoDesc", icon: "⛓️", category: "investing", lessons: 4 },
  { key: "careerGrowth", desc: "careerDesc", icon: "🎯", category: "career", lessons: 5 },
];

export default function Learning() {
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const { t } = useTranslations();

  const filtered = activeCategory === "all" ? TOPICS : TOPICS.filter(top => top.category === activeCategory);

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-800">{t("learning.title")}</h1>
        <p className="text-sm text-gray-400">{t("learning.subtitle")}</p>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
              activeCategory === cat ? "bg-sky-500 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {t(`learning.${cat}`)}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3">
        {[
          { icon: BookOpen, label: t("learning.articles"), to: "/articles" },
          { icon: Newspaper, label: t("learning.news"), to: "/news" },
          { icon: PenTool, label: t("learning.blog"), to: "/blog" },
          { icon: MessageSquare, label: t("learning.forum"), to: "/forum" },
        ].map(({ icon: Icon, label, to }) => (
          <Link key={to} to={to} className="card flex items-center gap-3 !p-3 hover:shadow-md transition-shadow">
            <div className="w-9 h-9 rounded-xl bg-sky-50 flex items-center justify-center">
              <Icon className="w-4 h-4 text-sky-500" />
            </div>
            <span className="text-sm font-medium text-gray-700">{label}</span>
          </Link>
        ))}
      </div>

      <div>
        <h2 className="font-semibold text-gray-800 mb-3">{t("learning.topicsToExplore")}</h2>
        <div className="space-y-3">
          {filtered.map(topic => (
            <div key={topic.key} className="card flex items-start gap-3">
              <span className="text-2xl">{topic.icon}</span>
              <div className="flex-1">
                <h3 className="font-medium text-gray-800 text-sm">{t(`learning.${topic.key}`)}</h3>
                <p className="text-xs text-gray-400 mt-0.5">{t(`learning.${topic.desc}`)}</p>
                <p className="text-xs text-sky-500 mt-1">{topic.lessons} {t("learning.lessons")}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-r from-sky-500 to-sky-600 rounded-2xl p-4 text-white">
        <h3 className="font-semibold mb-1">{t("learning.trackProgress")}</h3>
        <p className="text-sm opacity-90">{t("learning.trackDesc")}</p>
        <Link to="/profile" className="inline-block mt-3 bg-white text-sky-600 text-xs font-semibold px-4 py-2 rounded-xl">
          {t("learning.trackProgress")}
        </Link>
      </div>

      <ChatWidget
        endpoint="/ai/advisor/chat"
        personaName="Kemi"
        personaRole="AI Financial Advisor"
        accent="from-sky-400 to-sky-600"
        iconBg="bg-gradient-to-r from-sky-500 to-sky-600"
        placeholder="Ask Kemi to explain a finance topic..."
        prompts={["Explain budgeting basics", "What is compound interest?", "How do I start investing?"]}
      />
    </div>
  );
}
