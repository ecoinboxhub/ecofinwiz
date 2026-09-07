import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { Shield, Users, TrendingUp, Bell, Search, Send, BarChart3, Activity } from "lucide-react";
import client from "../api/client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useTranslations } from "../i18n/useTranslations";
import ConfirmDialog from "../components/ConfirmDialog";

const DAY_OPTIONS = [
  { value: 7, label: "7 days" },
  { value: 14, label: "14 days" },
  { value: 30, label: "30 days" },
  { value: 90, label: "90 days" },
];

export default function Admin() {
  const { user } = useAuth();
  const { t } = useTranslations();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [notificationMsg, setNotificationMsg] = useState("");
  const [sending, setSending] = useState(false);
  const [growthDays, setGrowthDays] = useState(30);
  const [userGrowth, setUserGrowth] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    Promise.all([
      client.get("/admin/stats").catch(() => ({ data: {} })),
      client.get("/admin/users").catch(() => ({ data: [] })),
    ]).then(([statsRes, usersRes]) => {
      setStats(statsRes.data);
      setUsers(Array.isArray(usersRes.data) ? usersRes.data : []);
    });
  }, []);

  useEffect(() => {
    client.get(`/admin/stats/users/growth?days=${growthDays}`).then(({ data }) => {
      setUserGrowth(Array.isArray(data) ? data : data?.growth || []);
    }).catch(() => {});
  }, [growthDays]);

  useEffect(() => {
    client.get("/admin/analytics/summary?period_days=30").then(({ data }) => {
      setAnalytics(data);
    }).catch(() => {});
  }, []);

  const toggleActive = async (id: string, current: boolean) => {
    try { await client.patch(`/admin/users/${id}`, { is_active: !current }); setUsers(prev => prev.map(u => u.id === id ? { ...u, is_active: !current } : u)); } catch {}
  };

  const toggleAdmin = async (id: string, current: boolean) => {
    try { await client.patch(`/admin/users/${id}`, { is_admin: !current }); setUsers(prev => prev.map(u => u.id === id ? { ...u, is_admin: !current } : u)); } catch {}
  };

  const sendNotification = async () => {
    if (!notificationMsg.trim()) return;
    setSending(true);
    try {
      const userIds = users.map((u: any) => u.id);
      await client.post("/admin/notifications/send", { user_ids: userIds, title: "Admin Announcement", body: notificationMsg, type: "admin" });
      setNotificationMsg("");
    } catch {}
    setSending(false);
    setShowConfirm(false);
  };

  const filteredUsers = users.filter((u: any) => u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) || u.email?.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center gap-2">
        <Shield className="w-6 h-6 text-sky-500" />
        <div>
          <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">{t("admin.title")}</h1>
          <p className="text-xs text-gray-400 dark:text-gray-500">{t("admin.welcome")}{user?.full_name}</p>
        </div>
      </div>

      {stats && (
        <>
          <div className="grid grid-cols-2 gap-3">
            <div className="card !p-4"><p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{t("admin.totalUsers")}</p><p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{stats.total_users || 0}</p></div>
            <div className="card !p-4"><p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{t("admin.activeToday")}</p><p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{stats.active_today || 0}</p></div>
            <div className="card !p-4"><p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{t("admin.transactions")}</p><p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{stats.total_transactions || 0}</p></div>
            <div className="card !p-4"><p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{t("admin.budgets")}</p><p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{stats.total_budgets || 0}</p></div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-800 dark:text-gray-100 text-sm">{t("admin.userGrowth")}</h3>
              <select value={growthDays} onChange={e => setGrowthDays(Number(e.target.value))} className="text-xs border border-gray-200 dark:border-gray-600 rounded-lg px-2 py-1 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                {DAY_OPTIONS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
              </select>
            </div>
            {userGrowth.length > 0 ? (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={userGrowth}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#9ca3af" }} />
                  <YAxis tick={{ fontSize: 10, fill: "#9ca3af" }} />
                  <Tooltip contentStyle={{ borderRadius: "12px", border: "1px solid #e5e7eb", fontSize: "12px" }} />
                  <Bar dataKey="count" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-8">{t("admin.noData")}</p>
            )}
          </div>

          {analytics && (
            <div className="grid grid-cols-2 gap-3">
              <div className="card !p-4"><p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{t("admin.newUsers")}</p><p className="text-lg font-bold text-gray-800 dark:text-gray-100">{analytics.new_users || 0}</p></div>
              <div className="card !p-4"><p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{t("admin.topCategory")}</p><p className="text-lg font-bold text-gray-800 dark:text-gray-100">{analytics.top_categories?.[0]?.category || t("admin.na")}</p></div>
            </div>
          )}
        </>
      )}

      <div className="card space-y-3">
        <h3 className="font-semibold text-gray-800 dark:text-gray-100 text-sm flex items-center gap-2"><Bell className="w-4 h-4 text-sky-500" /> {t("admin.broadcast")}</h3>
        <textarea className="input-field min-h-[80px]" placeholder={t("admin.messagePlaceholder")} value={notificationMsg} onChange={e => setNotificationMsg(e.target.value)} />
        <button onClick={() => setShowConfirm(true)} disabled={!notificationMsg.trim()} className="btn-primary w-full flex items-center justify-center gap-2">
          <Send className="w-4 h-4" /> {t("admin.sendToAll")}
        </button>
      </div>

      <ConfirmDialog
        open={showConfirm}
        title="Confirm Broadcast"
        message={`Send "${notificationMsg.slice(0, 60)}${notificationMsg.length > 60 ? "..." : ""}" to all ${users.length} users?`}
        confirmLabel="Send to All"
        onConfirm={sendNotification}
        onCancel={() => setShowConfirm(false)}
        loading={sending}
      />

      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-800 dark:text-gray-100 text-sm">{t("admin.users")}</h3>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
            <input className="pl-8 pr-3 py-1.5 text-sm border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-400 bg-gray-50 dark:bg-gray-700 dark:text-gray-100" placeholder={t("admin.searchPlaceholder")} value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
          </div>
        </div>
        <div className="space-y-2">
          {filteredUsers.slice(0, 20).map((u: any) => (
            <div key={u.id} className="card !p-3 flex items-center justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 rounded-full bg-sky-100 dark:bg-sky-900/50 flex items-center justify-center text-sky-600 dark:text-sky-400 font-semibold text-xs flex-shrink-0">
                  {u.full_name?.charAt(0) || t("admin.avatarFallback")}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">{u.full_name}</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 truncate">{u.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <button onClick={() => toggleActive(u.id, u.is_active)} className={`text-xs px-2 py-1 rounded-lg font-medium ${u.is_active ? "bg-green-50 dark:bg-green-900/40 text-green-600 dark:text-green-400" : "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400"}`}>
                  {u.is_active ? t("admin.active") : t("admin.inactive")}
                </button>
                <button onClick={() => toggleAdmin(u.id, u.is_admin)} className={`text-xs px-2 py-1 rounded-lg font-medium ${u.is_admin ? "bg-sky-50 dark:bg-sky-900/40 text-sky-600 dark:text-sky-400" : "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400"}`}>
                  {u.is_admin ? t("admin.admin") : t("admin.user")}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
