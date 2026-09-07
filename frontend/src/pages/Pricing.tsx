import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Check, Sparkles, Star, Crown } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";

const plans = [
  {
    key: "free",
    icon: Sparkles,
    priceKey: "freePrice",
    features: ["freeFeature1", "freeFeature2", "freeFeature3"],
  },
  {
    key: "premium",
    icon: Star,
    priceKey: "premiumPrice",
    features: ["premiumFeature1", "premiumFeature2", "premiumFeature3", "premiumFeature4", "premiumFeature5"],
    popular: true,
  },
  {
    key: "enterprise",
    icon: Crown,
    priceKey: "enterprisePrice",
    features: ["enterpriseFeature1", "enterpriseFeature2", "enterpriseFeature3", "enterpriseFeature4", "enterpriseFeature5", "enterpriseFeature6"],
  },
];

export default function Pricing() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslations();

  const subscribe = async (planKey: string) => {
    if (!user) return navigate("/login");
    if (planKey === "free") {
      try { await client.post("/payment/free"); } catch {}
      return;
    }
    try {
      const { data } = await client.post("/payment/initiate", { plan: planKey });
      if (data.authorization_url) window.location.href = data.authorization_url;
    } catch {}
  };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{t("pricing.title")}</h1>
        <p className="text-sm text-gray-400 mt-1">{t("pricing.subtitle")}</p>
      </div>

      <div className="space-y-4">
        {plans.map((plan) => {
          const Icon = plan.icon;
          return (
            <div key={plan.key} className={`card !p-5 relative ${plan.popular ? "ring-2 ring-sky-400" : ""}`}>
              {plan.popular && <span className="absolute -top-2.5 right-4 bg-sky-500 text-white text-xs font-semibold px-3 py-0.5 rounded-full">{t("pricing.popular")}</span>}
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${plan.key === "free" ? "bg-gray-100" : plan.key === "premium" ? "bg-sky-50" : "bg-amber-50"}`}>
                  <Icon className={`w-5 h-5 ${plan.key === "free" ? "text-gray-500" : plan.key === "premium" ? "text-sky-500" : "text-amber-500"}`} />
                </div>
                <div>
                  <h3 className="font-bold text-gray-800">{t("pricing." + plan.key)}</h3>
                  <p className="text-xs text-gray-400">{t("pricing." + plan.priceKey)}</p>
                </div>
              </div>
              <ul className="space-y-2 mb-4">
                {plan.features.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-500">
                    <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" /> {t("pricing." + f)}
                  </li>
                ))}
              </ul>
              <button onClick={() => subscribe(plan.key)} className={`w-full py-2.5 rounded-xl font-semibold text-sm ${plan.popular ? "btn-primary" : "btn-secondary"}`}>
                {t("pricing." + (plan.key === "free" ? "getStarted" : "subscribe"))}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
