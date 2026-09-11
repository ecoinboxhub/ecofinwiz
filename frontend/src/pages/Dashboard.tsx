import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { TrendingUp, Wallet, PiggyBank, ArrowUpRight, ArrowDownRight, Sparkles, BookOpen, Briefcase, LineChart, Bell, X } from "lucide-react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useTranslations } from "../i18n/useTranslations";

interface DashboardData {
  budget_summary: { total_budget: number; total_spent: number; remaining: number; budget_count: number };
  recent_transactions: any[];
  savings_summary: { total_goal: number; total_saved: number; goal_count: number };
  daily_tip: { tip: string; category: string };
}

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const { t } = useTranslations();
  const [dismissVerify, setDismissVerify] = useState(false);
  const isSme = user?.persona_type === "sme";

  useEffect(() => {
    Promise.allSettled([
      client.get("/finance/budgets/summary"),
      client.get("/finance/transactions?limit=5"),
      client.get("/finance/savings-goals"),
      client.get("/tips/daily"),
    ]).then(([budget, txns, savings, tip]) => {
      const budgetData = budget.status === "fulfilled" ? budget.value?.data : null;
      const txnsData = txns.status === "fulfilled" ? txns.value?.data : null;
      const savingsData = savings.status === "fulfilled" ? savings.value?.data : null;
      const tipData = tip.status === "fulfilled" ? tip.value?.data : null;
      const b = budgetData || { total_budget: 0, total_spent: 0, remaining: 0, budget_count: 0 };
      const savingsList: any[] = Array.isArray(savingsData) ? savingsData : savingsData?.goals ?? [];
      const totalGoal = savingsList.reduce((s: number, g: any) => s + (g.target_amount || 0), 0);
      const totalSaved = savingsList.reduce((s: number, g: any) => s + (g.current_amount || 0), 0);
      setData({
        budget_summary: b,
        recent_transactions: Array.isArray(txnsData) ? txnsData : txnsData?.transactions ?? [],
        savings_summary: { total_goal: totalGoal, total_saved: totalSaved, goal_count: savingsList.length },
        daily_tip: tipData || { tip: t("dashboard.dailyTip"), category: t("dashboard.finance") },
      });
    });
  }, []);

  const spentPct = data?.budget_summary.total_budget ? Math.round((data.budget_summary.total_spent / data.budget_summary.total_budget) * 100) : 0;
  const savedPct = data?.savings_summary.total_goal ? Math.round((data.savings_summary.total_saved / data.savings_summary.total_goal) * 100) : 0;

  const personalActions = [
    { to: "/transactions", icon: TrendingUp, label: t("dashboard.addTransaction"), color: "bg-sky-50 text-sky-500" },
    { to: "/budget", icon: Wallet, label: t("dashboard.setBudget"), color: "bg-gold-50 text-gold-500" },
    { to: "/savings", icon: PiggyBank, label: t("dashboard.createGoal"), color: "bg-orange-50 text-orange-500" },
    { to: "/advisor", icon: Sparkles, label: t("dashboard.kemiAI"), color: "bg-rose-50 text-rose-500" },
    { to: "/investment", icon: LineChart, label: t("dashboard.musaInvest"), color: "bg-emerald-50 text-emerald-500" },
    { to: "/learning", icon: BookOpen, label: t("dashboard.learn"), color: "bg-sky-50 text-sky-500" },
    { to: "/business", icon: Briefcase, label: t("dashboard.business"), color: "bg-gold-50 text-gold-500" },
  ];

  const smeActions = [
    { to: "/business", icon: Briefcase, label: "Business Tasks", color: "bg-gold-50 text-gold-500" },
    { to: "/invoices", icon: Wallet, label: "Invoices", color: "bg-sky-50 text-sky-500" },
    { to: "/business-plan", icon: LineChart, label: "Business Plan", color: "bg-emerald-50 text-emerald-500" },
    { to: "/mentor", icon: Sparkles, label: "Chidi AI", color: "bg-rose-50 text-rose-500" },
    { to: "/transactions", icon: TrendingUp, label: "Transactions", color: "bg-orange-50 text-orange-500" },
    { to: "/savings", icon: PiggyBank, label: "Savings", color: "bg-purple-50 text-purple-500" },
    { to: "/learning", icon: BookOpen, label: "Learn", color: "bg-sky-50 text-sky-500" },
  ];

  const quickActions = isSme ? smeActions : personalActions;

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-6">
      {!dismissVerify && user && !user.is_email_verified && (
        <div className="bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-700 rounded-2xl p-4 flex items-start gap-3">
          <Bell className="w-5 h-5 text-amber-500 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-800 dark:text-amber-200">Verify your email</p>
            <p className="text-xs text-amber-600 dark:text-amber-400 mt-0.5">Check your inbox for the verification link.</p>
          </div>
          <button onClick={() => setDismissVerify(true)} className="p-1 hover:bg-amber-100 dark:hover:bg-amber-800/50 rounded-lg" aria-label="Dismiss"><X className="w-4 h-4 text-amber-400" /></button>
        </div>
      )}

      <div>
        <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">{isSme ? "Your Business" : t("dashboard.welcomeBack")}{user ? `, ${user.full_name.split(" ")[0]}` : ""}!</h1>
        <p className="text-sm text-gray-400 dark:text-gray-500">{isSme ? "Manage invoices, tasks, and business growth" : t("dashboard.snapshot")}</p>
      </div>

      {data?.daily_tip && (
        <div className="bg-gradient-to-r from-sky-500 to-sky-600 rounded-2xl p-4 text-white">
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-4 h-4" />
            <span className="text-xs font-medium uppercase tracking-wide">{data.daily_tip.category}</span>
          </div>
          <p className="text-sm opacity-90">{data.daily_tip.tip}</p>
        </div>
      )}

      {!isSme && (
        <div className="grid grid-cols-2 gap-3">
          <div className="card">
            <div className="flex items-center gap-2 text-sm text-gray-400 dark:text-gray-500 mb-2">
              <Wallet className="w-4 h-4" /> {t("dashboard.budget")}
            </div>
            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">${(data?.budget_summary.remaining ?? 0).toLocaleString()}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500">{t("dashboard.ofLeft", (data?.budget_summary.total_budget ?? 0).toLocaleString())}</p>
            <div className="mt-2 h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden" role="img" aria-label={`Budget: ${spentPct}% spent`}>
              <div className={`h-full rounded-full transition-all ${spentPct > 90 ? "bg-rose-500" : "bg-sky-500"}`} style={{ width: `${spentPct}%` }} />
            </div>
          </div>
          <div className="card">
            <div className="flex items-center gap-2 text-sm text-gray-400 dark:text-gray-500 mb-2">
              <PiggyBank className="w-4 h-4" /> {t("dashboard.savings")}
            </div>
            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">${(data?.savings_summary.total_saved ?? 0).toLocaleString()}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500">{t("dashboard.ofGoal", (data?.savings_summary.total_goal ?? 0).toLocaleString())}</p>
            <div className="mt-2 h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden" role="img" aria-label={`Savings: ${savedPct}% of goal`}>
              <div className="h-full bg-gold-400 rounded-full transition-all" style={{ width: `${savedPct}%` }} />
            </div>
          </div>
        </div>
      )}

      {isSme && (
        <div className="card bg-gradient-to-r from-gold-50 dark:from-gold-900/20 to-amber-50 dark:to-amber-900/20 border-gold-100 dark:border-gold-800">
          <div className="flex items-center gap-2 mb-3">
            <Briefcase className="w-5 h-5 text-gold-500" />
            <h2 className="font-semibold text-gray-800 dark:text-gray-100">Business Overview</h2>
          </div>
          <div className="grid grid-cols-2 gap-3 text-center">
            <Link to="/invoices" className="bg-white dark:bg-gray-700 rounded-xl p-3 hover:shadow-sm transition-shadow">
              <p className="text-xl font-bold text-gold-500">{data?.budget_summary.budget_count || 0}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Invoices</p>
            </Link>
            <Link to="/business" className="bg-white dark:bg-gray-700 rounded-xl p-3 hover:shadow-sm transition-shadow">
              <p className="text-xl font-bold text-sky-500">0</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Tasks</p>
            </Link>
          </div>
        </div>
      )}

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-800 dark:text-gray-100">{t("dashboard.quickActions")}</h2>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {quickActions.map(({ to, icon: Icon, label, color }) => (
            <Link key={to} to={to} className={`${color} rounded-xl p-3 flex flex-col items-center gap-1.5 text-center transition-all active:scale-95`}>
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{label}</span>
            </Link>
          ))}
        </div>
      </div>

      {!isSme && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-gray-800 dark:text-gray-100">{t("dashboard.recentTransactions")}</h2>
            <Link to="/transactions" className="text-xs text-sky-500 font-medium">{t("dashboard.seeAll")}</Link>
          </div>
          <div className="space-y-2">
            {(data?.recent_transactions ?? []).length === 0 ? (
              <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-6">{t("dashboard.noTransactions")}</p>
            ) : (
              data?.recent_transactions.slice(0, 5).map((tx: any) => (
                <div key={tx.id} className="card !p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center ${tx.type === "income" ? "bg-green-50 dark:bg-green-900/30" : "bg-rose-50 dark:bg-rose-900/30"}`}>
                      {tx.type === "income" ? <ArrowUpRight className="w-4 h-4 text-green-500" /> : <ArrowDownRight className="w-4 h-4 text-rose-500" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-800 dark:text-gray-100">{tx.description || tx.category_name || t("dashboard.transaction")}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500">{new Date(tx.date || tx.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <span className={`font-semibold text-sm ${tx.type === "income" ? "text-green-600 dark:text-green-400" : "text-rose-600 dark:text-rose-400"}`}>
                    {tx.type === "income" ? "+" : "-"}${Math.abs(tx.amount).toLocaleString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
