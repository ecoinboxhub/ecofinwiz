import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { Plus, PiggyBank, Target, Trash2 } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function Savings() {
  const { t } = useTranslations();
  const [goals, setGoals] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [target, setTarget] = useState("");
  const [contribution, setContribution] = useState("");

  const fetchGoals = async () => {
    try {
      const { data } = await client.get("/finance/savings-goals");
      setGoals(Array.isArray(data) ? data : data?.goals || []);
    } catch { setGoals([]); }
  };

  useEffect(() => { fetchGoals(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post("/finance/savings-goals", { name, target_amount: Number(target), monthly_contribution: contribution ? Number(contribution) : null });
      setShowForm(false);
      setName(""); setTarget(""); setContribution("");
      fetchGoals();
      toast.success("Savings goal created");
    } catch { toast.error("Failed to create goal"); }
  };

  const handleContribute = async (id: string) => {
    const amt = prompt("Contribution amount:");
    if (!amt) return;
    try { await client.post(`/finance/savings-goals/${id}/contribute`, { amount: Number(amt) }); fetchGoals(); toast.success("Contribution added"); } catch { toast.error("Failed to add contribution"); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t("savings.deleteConfirm"))) return;
    try { await client.delete(`/finance/savings-goals/${id}`); fetchGoals(); toast.success("Goal deleted"); } catch { toast.error("Failed to delete goal"); }
  };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("savings.title")}</h1>
          <p className="text-sm text-gray-400">{t("savings.goals", goals.length.toString())}</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary !p-3 !rounded-xl">
          <Plus className="w-5 h-5" />
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-3">
          <h3 className="font-semibold text-gray-800">{t("savings.new")}</h3>
          <input className="input-field" placeholder={t("savings.namePlaceholder")} value={name} onChange={e => setName(e.target.value)} required />
          <input type="number" className="input-field" placeholder={t("savings.targetPlaceholder")} value={target} onChange={e => setTarget(e.target.value)} required min="0" step="0.01" />
          <input type="number" className="input-field" placeholder={t("savings.contributionPlaceholder")} value={contribution} onChange={e => setContribution(e.target.value)} min="0" step="0.01" />
          <div className="flex gap-2">
            <button type="submit" className="btn-primary flex-1">{t("savings.create")}</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">{t("common.cancel")}</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {goals.length === 0 ? (
          <div className="text-center py-10">
            <PiggyBank className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{t("savings.empty")}</p>
          </div>
        ) : goals.map((g) => {
          const pct = g.target_amount > 0 ? Math.min((g.current_amount / g.target_amount) * 100, 100) : 0;
          return (
            <div key={g.id} className="card">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gold-50 flex items-center justify-center text-gold-500">
                    <Target className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800 text-sm">{g.name}</p>
                    <p className="text-xs text-gray-400">{g.monthly_contribution ? `$${g.monthly_contribution}${t("savings.perMonth")}` : t("savings.noMonthlyGoal")}</p>
                  </div>
                </div>
                <button onClick={() => handleDelete(g.id)} className="p-1.5 hover:bg-rose-50 rounded-lg transition-colors">
                  <Trash2 className="w-3.5 h-3.5 text-rose-400" />
                </button>
              </div>
              <div className="flex items-center justify-between text-sm mb-1.5">
                <span className="text-gray-500">${Number(g.current_amount).toLocaleString()}{t("savings.saved")}</span>
                <span className="font-medium text-gray-700">${Number(g.target_amount).toLocaleString()}</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-3">
                <div className="h-full rounded-full bg-gradient-to-r from-gold-300 to-gold-500" style={{ width: `${pct}%` }} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">{Math.round(pct)}{t("savings.percentComplete")}</span>
                <button onClick={() => handleContribute(g.id)} className="text-xs bg-gold-400 text-white px-3 py-1.5 rounded-lg font-medium hover:bg-gold-500 transition-colors">
                  {t("savings.contribute")}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <ChatWidget
        endpoint="/ai/advisor/chat"
        personaName="Kemi"
        personaRole="AI Financial Advisor"
        accent="from-sky-400 to-sky-600"
        iconBg="bg-gradient-to-r from-sky-500 to-sky-600"
        placeholder="Ask Kemi about your savings..."
        prompts={["Create a savings goal of $1000", "How much have I saved?", "Tips to reach my goal faster"]}
      />
    </div>
  );
}
