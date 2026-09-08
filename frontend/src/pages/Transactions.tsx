import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { ArrowUpRight, ArrowDownRight, Plus, X } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function Transactions() {
  const { t } = useTranslations();
  const [txns, setTxns] = useState<any[]>([]);
  const [filter, setFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ type: "expense", amount: "", description: "", category_name: "", date: new Date().toISOString().split("T")[0] });

  const fetchTxns = async () => {
    try {
      const params: any = { limit: 50 };
      if (filter !== "all") params.type = filter;
      const { data } = await client.get("/finance/transactions", { params });
      setTxns(Array.isArray(data) ? data : data?.transactions || []);
    } catch { setTxns([]); }
  };

  useEffect(() => { fetchTxns(); }, [filter]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post("/finance/transactions", { ...form, amount: Number(form.amount) });
      setShowForm(false);
      setForm({ type: "expense", amount: "", description: "", category_name: "", date: new Date().toISOString().split("T")[0] });
      fetchTxns();
      toast.success("Transaction added");
    } catch { toast.error("Failed to add transaction"); }
  };

  const totalIncome = txns.filter(t => t.type === "income").reduce((s, t) => s + Number(t.amount), 0);
  const totalExpense = txns.filter(t => t.type === "expense").reduce((s, t) => s + Number(t.amount), 0);

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("transactions.title")}</h1>
          <p className="text-sm text-gray-400">{t("transactions.entries", txns.length.toString())}</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary !p-3 !rounded-xl" aria-label={t("transactions.add")}>
          <Plus className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="card">
          <p className="text-xs text-gray-400 mb-1">{t("transactions.income")}</p>
          <p className="text-lg font-bold text-green-600">+${totalIncome.toLocaleString()}</p>
        </div>
        <div className="card">
          <p className="text-xs text-gray-400 mb-1">{t("transactions.expenses")}</p>
          <p className="text-lg font-bold text-rose-600">-${totalExpense.toLocaleString()}</p>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-3 relative">
          <button type="button" onClick={() => setShowForm(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"><X className="w-4 h-4" /></button>
          <h3 className="font-semibold text-gray-800">{t("transactions.new")}</h3>
          <div className="flex gap-2">
            <button type="button" onClick={() => setForm({ ...form, type: "expense" })} className={`flex-1 py-2 rounded-xl text-sm font-medium transition-all ${form.type === "expense" ? "bg-rose-500 text-white" : "bg-gray-100 text-gray-600"}`}>{t("transactions.expense")}</button>
            <button type="button" onClick={() => setForm({ ...form, type: "income" })} className={`flex-1 py-2 rounded-xl text-sm font-medium transition-all ${form.type === "income" ? "bg-green-500 text-white" : "bg-gray-100 text-gray-600"}`}>{t("transactions.income")}</button>
          </div>
          <input type="number" className="input-field" placeholder={t("transactions.amountPlaceholder")} value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })} required min="0" step="0.01" />
          <input className="input-field" placeholder={t("transactions.descriptionPlaceholder")} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
          <input className="input-field" placeholder={t("transactions.categoryPlaceholder")} value={form.category_name} onChange={e => setForm({ ...form, category_name: e.target.value })} />
          <input type="date" className="input-field" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} />
          <button type="submit" className="btn-primary w-full">{t("transactions.add")}</button>
        </form>
      )}

      <div className="flex gap-2 overflow-x-auto pb-1">
        {["all", "income", "expense"].map(f => (
          <button key={f} onClick={() => setFilter(f)} className={`px-4 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${filter === f ? "bg-sky-500 text-white" : "bg-gray-100 text-gray-500"}`}>
            {f === "all" ? t("transactions.filterAll") : f === "income" ? t("transactions.filterIncome") : t("transactions.filterExpense")}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {txns.length === 0 ? (
          <p className="text-center text-gray-400 text-sm py-8">{t("transactions.empty")}</p>
        ) : txns.map((tx: any) => (
          <div key={tx.id} className="card !p-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center ${tx.type === "income" ? "bg-green-50" : "bg-rose-50"}`}>
                {tx.type === "income" ? <ArrowUpRight className="w-4 h-4 text-green-500" /> : <ArrowDownRight className="w-4 h-4 text-rose-500" />}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">{tx.description || tx.category_name || t("dashboard.transaction")}</p>
                <p className="text-xs text-gray-400">{tx.category_name} &middot; {new Date(tx.date || tx.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            <span className={`font-semibold text-sm ${tx.type === "income" ? "text-green-600" : "text-rose-600"}`}>
              {tx.type === "income" ? "+" : "-"}${Math.abs(tx.amount).toLocaleString()}
            </span>
          </div>
        ))}
      </div>

      <ChatWidget
        endpoint="/ai/advisor/chat"
        personaName="Kemi"
        personaRole="AI Financial Advisor"
        accent="from-sky-400 to-sky-600"
        iconBg="bg-gradient-to-r from-sky-500 to-sky-600"
        placeholder="Ask Kemi about your transactions..."
        prompts={["Record a transaction of $50 for food", "What did I spend this month?", "Categorize my recent expenses"]}
      />
    </div>
  );
}
