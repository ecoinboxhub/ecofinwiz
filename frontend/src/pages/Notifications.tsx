import { useState, useEffect } from "react";
import { Bell, CheckCheck, Sparkles, TrendingUp, Wallet, MessageCircle } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";

export default function Notifications() {
  const { t } = useTranslations();
  const [notifications, setNotifications] = useState<any[]>([]);

  useEffect(() => { client.get("/users/me/notifications").then(({ data }) => setNotifications(Array.isArray(data) ? data : [])).catch(() => {}); }, []);

  const markRead = async (id: string) => {
    try { await client.patch(`/users/me/notifications/${id}/read`); } catch {}
  };

  const markAllRead = async () => {
    try { await client.post("/users/me/notifications/read-all"); setNotifications(prev => prev.map(n => ({ ...n, is_read: true }))); } catch {}
  };

  const iconMap: Record<string, any> = { tip: Sparkles, finance: TrendingUp, budget: Wallet, ai: MessageCircle };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("notifications.title")}</h1>
          <p className="text-sm text-gray-400">{t("notifications.unread", notifications.filter(n => !n.is_read).length.toString())}</p>
        </div>
        <button onClick={markAllRead} className="text-sm text-sky-500 font-medium flex items-center gap-1"><CheckCheck className="w-4 h-4" /> {t("notifications.markAll")}</button>
      </div>

      <div className="space-y-2">
        {notifications.length === 0 ? (
          <div className="text-center py-10">
            <Bell className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{t("notifications.empty")}</p>
          </div>
        ) : notifications.map((n: any) => {
          const Icon = iconMap[n.category] || Bell;
          return (
            <div key={n.id} className={`card !p-4 flex items-start gap-3 ${!n.is_read ? "border-l-4 border-l-sky-500" : ""}`} onClick={() => !n.is_read && markRead(n.id)}>
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${n.is_read ? "bg-gray-100" : "bg-sky-50"}`}>
                <Icon className={`w-4 h-4 ${n.is_read ? "text-gray-400" : "text-sky-500"}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm ${n.is_read ? "text-gray-500" : "text-gray-800 font-medium"}`}>{n.message || n.title}</p>
                <p className="text-xs text-gray-400 mt-1">{n.created_at ? new Date(n.created_at).toLocaleDateString() : ""}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
