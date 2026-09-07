import { useState } from "react";
import toast from "react-hot-toast";
import { FileText, Sparkles } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function BusinessPlan() {
  const { t } = useTranslations();
  const [businessName, setBusinessName] = useState("");
  const [industry, setIndustry] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<any>(null);

  const generate = async () => {
    if (!businessName.trim() || !industry.trim() || !description.trim()) return;
    setLoading(true);
    setPlan(null);
    try {
      const { data } = await client.post("/business-plans/generate", {
        business_name: businessName, industry, description,
      });
      setPlan(data);
      toast.success("Business plan generated");
    } catch {
      toast.error(t("businessPlan.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center gap-2">
        <FileText className="w-6 h-6 text-gold-500" />
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("businessPlan.title")}</h1>
          <p className="text-sm text-gray-400">{t("businessPlan.subtitle")}</p>
        </div>
      </div>

      <div className="card space-y-3">
        <label className="text-sm font-medium text-gray-600">Business Name</label>
        <input className="input-field" placeholder="e.g. Artisan Hub Africa" value={businessName} onChange={e => setBusinessName(e.target.value)} />

        <label className="text-sm font-medium text-gray-600">Industry</label>
        <input className="input-field" placeholder="e.g. E-commerce / Technology" value={industry} onChange={e => setIndustry(e.target.value)} />

        <label className="text-sm font-medium text-gray-600">Description</label>
        <textarea className="input-field min-h-[100px]" placeholder="Describe your business idea in detail..." value={description} onChange={e => setDescription(e.target.value)} />

        <button onClick={generate} disabled={loading || !businessName.trim() || !industry.trim() || !description.trim()} className="btn-gold w-full flex items-center justify-center gap-2">
          {loading ? <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" /> : <><Sparkles className="w-4 h-4" /> {t("businessPlan.generate")}</>}
        </button>
      </div>

      {plan && (
        <div className="card space-y-4">
          <h2 className="font-bold text-lg text-gray-800">{plan.business_name || t("businessPlan.yourPlan")}</h2>
          {plan.executive_summary && <div><h3 className="font-semibold text-sm text-gray-600 mb-1">{t("businessPlan.execSummary")}</h3><p className="text-sm text-gray-500">{plan.executive_summary}</p></div>}
          {plan.mission && <div><h3 className="font-semibold text-sm text-gray-600 mb-1">{t("businessPlan.mission")}</h3><p className="text-sm text-gray-500">{plan.mission}</p></div>}
          {plan.market_analysis && <div><h3 className="font-semibold text-sm text-gray-600 mb-1">{t("businessPlan.marketAnalysis")}</h3><p className="text-sm text-gray-500">{plan.market_analysis}</p></div>}
          {plan.revenue_model && <div><h3 className="font-semibold text-sm text-gray-600 mb-1">{t("businessPlan.revenueModel")}</h3><p className="text-sm text-gray-500">{plan.revenue_model}</p></div>}
          <button className="btn-primary w-full">{t("businessPlan.savePlan")}</button>
        </div>
      )}

      <ChatWidget
        endpoint="/ai/mentor/chat"
        personaName="Chidi"
        personaRole="AI Business Mentor"
        accent="from-gold-400 to-gold-600"
        iconBg="bg-gradient-to-r from-gold-500 to-gold-600"
        placeholder="Ask Chidi to help shape your business plan..."
        prompts={["Generate a business plan for my cafe", "What sections should my plan include?", "Help me refine my revenue model"]}
      />
    </div>
  );
}
