import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { Plus, Wallet, Edit2, Trash2, Target, TrendingUp } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

interface Budget {
  id: string; category: string; amount: number; spent: number; period: string; month: string;
}

export default function Budget() {
  const { t } = useTranslations();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [category, setCategory] = useState("");
  const [amount, setAmount] = useState("");
  const [period, setPeriod] = useState("monthly");
  const [editing, setEditing] = useState<string | null>(null);

  const fetchBudgets = async () => {
    try {
      const { data } = await client.get("/finance/budgets");
      setBudgets(Array.isArray(data) ? data : data?.budgets || []);
    } catch { setBudgets([]); }
  };

  useEffect(() => { fetchBudgets(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) {
        await client.patch(`/finance/budgets/${editing}`, { category, amount: Number(amount), period });
      } else {
        await client.post("/finance/budgets", { category, amount: Number(amount), period });
      }
      setShowForm(false);
      setEditing(null);
      setCategory("");
      setAmount("");
      setPeriod("monthly");
      fetchBudgets();
      toast.success(editing ? "Budget updated" : "Budget created");
    } catch { toast.error("Failed to save budget"); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t("budget.deleteConfirm"))) return;
    try { await client.delete(`/finance/budgets/${id}`); fetchBudgets(); toast.success("Budget deleted"); } catch { toast.error("Failed to delete budget"); }
  };

  const startEdit = (b: Budget) => {
    setCategory(b.category);
    setAmount(String(b.amount));
    setPeriod(b.period);
    setEditing(b.id);
    setShowForm(true);
  };

  const totalBudget = budgets.reduce((s, b) => s + b.amount, 0);
  const totalSpent = budgets.reduce((s, b) => s + b.spent, 0);

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("budget.title")}</h1>
          <p className="text-sm text-gray-400">{t("budget.activeBudgets", budgets.length.toString())}</p>
        </div>
        <button onClick={() => { setShowForm(true); setEditing(null); setCategory(""); setAmount(""); setPeriod("monthly"); }} className="btn-primary !p-3 !rounded-xl" aria-label={t("budget.create")}>
          <Plus className="w-5 h-5" />
        </button>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Wallet className="w-4 h-4" /> {t("budget.totalBudget")}
          </div>
          <span className="text-lg font-bold text-gray-800">${totalBudget.toLocaleString()}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">{t("budget.spent")}${totalSpent.toLocaleString()}</span>
          <span className={totalBudget - totalSpent >= 0 ? "text-green-600 font-medium" : "text-rose-600 font-medium"}>
            ${(totalBudget - totalSpent).toLocaleString()}{t("budget.left")}
          </span>
        </div>
        <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all ${totalBudget > 0 && totalSpent / totalBudget > 0.9 ? "bg-rose-500" : "bg-sky-500"}`}
            style={{ width: `${totalBudget > 0 ? Math.min((totalSpent / totalBudget) * 100, 100) : 0}%` }} />
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-3">
          <h3 className="font-semibold text-gray-800">{editing ? t("budget.edit") : t("budget.new")}</h3>
          <input className="input-field" placeholder={t("budget.categoryPlaceholder")} value={category} onChange={e => setCategory(e.target.value)} required />
          <input type="number" className="input-field" placeholder={t("budget.amountPlaceholder")} value={amount} onChange={e => setAmount(e.target.value)} required min="0" step="0.01" />
          <select className="input-field" value={period} onChange={e => setPeriod(e.target.value)}>
            <option value="monthly">{t("budget.monthly")}</option>
            <option value="weekly">{t("budget.weekly")}</option>
            <option value="yearly">{t("budget.yearly")}</option>
          </select>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary flex-1">{editing ? t("budget.update") : t("budget.create")}</button>
            <button type="button" onClick={() => { setShowForm(false); setEditing(null); }} className="btn-secondary flex-1">{t("common.cancel")}</button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {budgets.length === 0 ? (
          <div className="text-center py-10">
            <Wallet className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{t("budget.empty")}</p>
          </div>
        ) : budgets.map((b) => {
          const pct = b.amount > 0 ? Math.min((b.spent / b.amount) * 100, 100) : 0;
          return (
            <div key={b.id} className="card !p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-sky-50 flex items-center justify-center text-sky-500">
                    <Target className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800 text-sm">{b.category}</p>
                    <p className="text-xs text-gray-400 capitalize">{b.period}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => startEdit(b)} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"><Edit2 className="w-3.5 h-3.5 text-gray-400" /></button>
                  <button onClick={() => handleDelete(b.id)} className="p-1.5 hover:bg-rose-50 rounded-lg transition-colors"><Trash2 className="w-3.5 h-3.5 text-rose-400" /></button>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm mb-1.5">
                <span className="text-gray-500">${b.spent.toLocaleString()}{t("budget.spentSuffix")}</span>
                <span className="font-medium text-gray-700">${b.amount.toLocaleString()}</span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${pct > 90 ? "bg-rose-500" : "bg-sky-500"}`} style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>

      <Link to="/transactions" className="card !p-3 flex items-center justify-between hover:bg-gray-50 transition-colors">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">{t("budget.viewTransactions")}</span>
        </div>
        <span className="text-sky-500 text-sm font-medium">{t("budget.go")}</span>
      </Link>

      <ChatWidget
        endpoint="/ai/advisor/chat"
        personaName="Kemi"
        personaRole="AI Financial Advisor"
        accent="from-sky-400 to-sky-600"
        iconBg="bg-gradient-to-r from-sky-500 to-sky-600"
        placeholder="Ask Kemi about your budget..."
        prompts={["Create a budget for food", "What is my total budget?", "How can I reduce my spending?"]}
      />
    </div>
  );
}
