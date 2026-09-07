import { useState } from "react";
import toast from "react-hot-toast";
import {
  Calculator, Home, TrendingUp, PiggyBank, Landmark, FileText,
  Building2, LineChart, Percent, IndianRupee,
} from "lucide-react";
import client from "../api/client";
import ChatWidget from "../components/ChatWidget";
import { useTranslations } from "../i18n/useTranslations";

type Field = { key: string; labelKey: string; type?: string; step?: string; placeholder?: string };

const CALCULATORS: { key: string; nameKey: string; icon: any; endpoint: string; fields: Field[] }[] = [
  {
    key: "mortgage",
    nameKey: "mortgage",
    icon: Home,
    endpoint: "/calculators/mortgage",
    fields: [
      { key: "principal", labelKey: "loanAmount", type: "number", step: "0.01" },
      { key: "annual_rate_pct", labelKey: "annualRate", type: "number", step: "0.01" },
      { key: "term_years", labelKey: "termYears", type: "number" },
    ],
  },
  {
    key: "investment",
    nameKey: "investment",
    icon: TrendingUp,
    endpoint: "/calculators/investment",
    fields: [
      { key: "principal", labelKey: "initialInvestment", type: "number", step: "0.01" },
      { key: "annual_rate_pct", labelKey: "expectedReturn", type: "number", step: "0.01" },
      { key: "years", labelKey: "yearsHeld", type: "number" },
    ],
  },
  {
    key: "mutual_fund",
    nameKey: "mutualFund",
    icon: PiggyBank,
    endpoint: "/calculators/mutual-fund",
    fields: [
      { key: "initial_lump_sum", labelKey: "lumpSum", type: "number", step: "0.01", placeholder: "0" },
      { key: "monthly_contribution", labelKey: "monthlySip", type: "number", step: "0.01", placeholder: "0" },
      { key: "annual_rate_pct", labelKey: "expectedReturn", type: "number", step: "0.01" },
      { key: "years", labelKey: "years", type: "number" },
    ],
  },
  {
    key: "bond",
    nameKey: "bond",
    icon: Landmark,
    endpoint: "/calculators/bond",
    fields: [
      { key: "face_value", labelKey: "faceValue", type: "number", step: "0.01" },
      { key: "coupon_rate_pct", labelKey: "couponRate", type: "number", step: "0.01" },
      { key: "price", labelKey: "marketPrice", type: "number", step: "0.01" },
      { key: "years_to_maturity", labelKey: "yearsToMaturity", type: "number" },
    ],
  },
  {
    key: "treasury_bill",
    nameKey: "treasuryBill",
    icon: FileText,
    endpoint: "/calculators/treasury-bill",
    fields: [
      { key: "face_value", labelKey: "faceValue", type: "number", step: "0.01" },
      { key: "price", labelKey: "purchasePrice", type: "number", step: "0.01" },
      { key: "days", labelKey: "tenorDays", type: "number" },
    ],
  },
  {
    key: "commercial_paper",
    nameKey: "commercialPaper",
    icon: Building2,
    endpoint: "/calculators/commercial-paper",
    fields: [
      { key: "face_value", labelKey: "faceValue", type: "number", step: "0.01" },
      { key: "discount_rate_pct", labelKey: "discountRate", type: "number", step: "0.01" },
      { key: "days", labelKey: "tenorDaysShort", type: "number" },
    ],
  },
  {
    key: "real_estate",
    nameKey: "realEstate",
    icon: Building2,
    endpoint: "/calculators/real-estate",
    fields: [
      { key: "property_value", labelKey: "propertyValue", type: "number", step: "0.01" },
      { key: "annual_rent", labelKey: "annualRent", type: "number", step: "0.01" },
      { key: "annual_expenses", labelKey: "annualExpenses", type: "number", step: "0.01", placeholder: "0" },
      { key: "down_payment", labelKey: "downPayment", type: "number", step: "0.01" },
    ],
  },
  {
    key: "compound_interest",
    nameKey: "compoundInterest",
    icon: LineChart,
    endpoint: "/calculators/compound-interest",
    fields: [
      { key: "principal", labelKey: "startingAmount", type: "number", step: "0.01", placeholder: "0" },
      { key: "monthly_contribution", labelKey: "monthlyContribution", type: "number", step: "0.01" },
      { key: "annual_rate_pct", labelKey: "expectedReturn", type: "number", step: "0.01" },
      { key: "years", labelKey: "years", type: "number" },
    ],
  },
];

function fmt(n: number | undefined | null): string {
  if (n === undefined || n === null || Number.isNaN(Number(n))) return "-";
  return Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function ResultRow({ label, value, isMoney }: { label: string; value: number; isMoney?: boolean }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="font-semibold text-gray-800">
        {isMoney ? `₦${fmt(value)}` : `${fmt(value)}%`}
      </span>
    </div>
  );
}

export default function Calculators() {
  const { t } = useTranslations();
  const [active, setActive] = useState(CALCULATORS[0]);
  const [values, setValues] = useState<Record<string, string>>({});
  const [result, setResult] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(false);

  const switchTab = (calc: typeof CALCULATORS[number]) => {
    setActive(calc);
    setValues({});
    setResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const body: Record<string, number> = {};
    for (const f of active.fields) {
      const v = Number(values[f.key]);
      if (values[f.key] === "" || Number.isNaN(v)) {
        toast.error(t(`calculators.fillRequired`, t(`calculators.${f.labelKey}`)));
        return;
      }
      body[f.key] = v;
    }
    setLoading(true);
    try {
      const { data } = await client.post(active.endpoint, body);
      setResult(data);
    } catch {
      toast.error(t("calculators.failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div>
        <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <Calculator className="w-5 h-5 text-sky-500" /> {t("calculators.title")}
        </h1>
        <p className="text-sm text-gray-400">{t("calculators.subtitle")}</p>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {CALCULATORS.map((c) => (
          <button
            key={c.key}
            onClick={() => switchTab(c)}
            className={`shrink-0 px-3 py-2 rounded-xl text-xs font-medium transition-colors ${
              active.key === c.key
                ? "bg-sky-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {t(`calculators.${c.nameKey}`)}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="card space-y-3">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <active.icon className="w-4 h-4 text-sky-500" /> {t(`calculators.${active.nameKey}`)}
        </h3>
        {active.fields.map((f) => (
          <div key={f.key}>
            <label className="block text-xs font-medium text-gray-500 mb-1">{t(`calculators.${f.labelKey}`)}</label>
            <input
              type={f.type || "text"}
              step={f.step}
              placeholder={f.placeholder}
              className="input-field"
              value={values[f.key] ?? ""}
              onChange={(e) => setValues({ ...values, [f.key]: e.target.value })}
              required
            />
          </div>
        ))}
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? t("calculators.calculating") : t("calculators.calculate")}
        </button>
      </form>

      {result && (
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <Percent className="w-4 h-4 text-emerald-500" /> {t("calculators.results")}
          </h3>
          {Object.entries(result).map(([k, v]) => {
            const isMoney = /payment|payment|total|interest|value|coupon|income|profit|price|principal|investment/.test(k);
            return <ResultRow key={k} label={k.replace(/_/g, " ")} value={Number(v)} isMoney={isMoney} />;
          })}
        </div>
      )}

      <div className="flex items-center gap-2 text-xs text-gray-400 bg-gold-50 rounded-xl p-3">
        <IndianRupee className="w-4 h-4 text-gold-500" />
        {t("calculators.disclaimer")}
      </div>

      <ChatWidget
        endpoint="/ai/investment/chat"
        personaName="Musa"
        personaRole="AI Investment Advisor"
        accent="from-emerald-400 to-emerald-600"
        iconBg="bg-gradient-to-r from-emerald-500 to-emerald-600"
        placeholder="Ask Musa about investments..."
        prompts={["What should I invest in?", "Explain treasury bills", "Help me pick a mutual fund"]}
      />
    </div>
  );
}