import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles, Briefcase, TrendingUp, GraduationCap } from "lucide-react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

const PERSONAS = [
  { type: "freelancer", icon: Sparkles, label: "Freelancer", desc: "Track irregular income, manage expenses, save for goals", color: "from-sky-400 to-sky-600", bg: "bg-sky-50 border-sky-200" },
  { type: "sme", icon: Briefcase, label: "Business Owner", desc: "Manage invoices, tasks, business plans, and cash flow", color: "from-gold-400 to-gold-600", bg: "bg-gold-50 border-gold-200" },
  { type: "investor", icon: TrendingUp, label: "Investor", desc: "Learn investing, track savings goals, build wealth", color: "from-emerald-400 to-emerald-600", bg: "bg-emerald-50 border-emerald-200" },
  { type: "student", icon: GraduationCap, label: "Student", desc: "Learn financial literacy, budget on a small income", color: "from-purple-400 to-purple-600", bg: "bg-purple-50 border-purple-200" },
];

export default function Onboarding() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [selected, setSelected] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    document.title = "Welcome - Finwize";
    if (user?.onboarding_completed) navigate("/dashboard", { replace: true });
  }, [user]);

  const handleSubmit = async () => {
    if (!selected || saving) return;
    setSaving(true);
    try {
      await client.patch("/users/me", { persona_type: selected });
      await client.patch("/users/me/preferences", { persona_type: selected });
      window.location.href = selected === "sme" ? "/mentor" : "/advisor";
    } catch {
      window.location.href = "/dashboard";
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-sky-50 via-white to-gold-50">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-400 to-sky-600 flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">F</div>
          <h1 className="text-2xl font-bold text-gray-800">Welcome to Finwize!</h1>
          <p className="text-gray-500 text-sm mt-1">Tell us about yourself so we can tailor your experience.</p>
        </div>

        <div className="space-y-3">
          {PERSONAS.map(({ type, icon: Icon, label, desc, color, bg }) => (
            <button
              key={type}
              onClick={() => setSelected(type)}
              className={`w-full text-left p-4 rounded-2xl border-2 transition-all flex items-center gap-4 ${selected === type ? `${bg} border-sky-500 shadow-md` : "bg-white border-gray-100 hover:border-gray-200"}`}
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center flex-shrink-0`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-800">{label}</p>
                <p className="text-sm text-gray-400">{desc}</p>
              </div>
              {selected === type && <div className="w-6 h-6 rounded-full bg-sky-500 flex items-center justify-center"><svg className="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg></div>}
            </button>
          ))}
        </div>

        <button
          onClick={handleSubmit}
          disabled={!selected || saving}
          className="btn-primary w-full mt-6"
        >
          {saving ? "Setting up..." : "Get Started"}
        </button>

        <button
          onClick={() => window.location.href = "/dashboard"}
          className="w-full text-center text-sm text-gray-400 hover:text-gray-600 mt-4"
        >
          Skip for now
        </button>
      </div>
    </div>
  );
}
