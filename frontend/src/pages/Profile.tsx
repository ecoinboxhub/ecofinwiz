import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { Settings, Bell, Shield, LogOut, ChevronRight, BookOpen, Target, Crown, Star } from "lucide-react";
import { Link } from "react-router-dom";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";

export default function Profile() {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState({ completed_lessons: 0, badges: 0, savings_goals: 0 });
  const { t } = useTranslations();

  useEffect(() => {
    Promise.all([
      client.get("/users/me/progress").catch(() => ({ data: {} })),
    ]).then(([progress]) => {
      const p = progress.data || {};
      setStats({
        completed_lessons: p.completed_lessons || 0,
        badges: p.badges || 0,
        savings_goals: p.savings_goals || 0,
      });
    });
  }, []);

  const menuItems = [
    { icon: Crown, label: t("profile.upgradePlan"), to: "/pricing" },
    { icon: BookOpen, label: t("profile.myLearning"), to: "/learning" },
    { icon: Target, label: t("profile.myGoals"), to: "/savings" },
    { icon: Bell, label: t("profile.notifications"), to: "/notifications" },
    { icon: Shield, label: t("profile.privacySecurity"), to: "#" },
  ];

  if (user?.is_admin) menuItems.push({ icon: Settings, label: t("profile.adminDashboard"), to: "/admin" });

  const planLabel = user?.plan === "free" ? t("profile.freePlan") : user?.plan === "pro" ? t("profile.proPlan") : t("profile.businessPlan");

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-6">
      <div className="card text-center">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-sky-400 to-sky-600 flex items-center justify-center text-white font-bold text-2xl mx-auto mb-3">
          {user?.full_name?.charAt(0) || "U"}
        </div>
        <h1 className="text-xl font-bold text-gray-800">{user?.full_name || "User"}</h1>
        <p className="text-sm text-gray-400">{user?.email}</p>
        <div className="flex items-center justify-center gap-2 mt-2">
          {user?.is_admin && <span className="badge-sky inline-block">{t("profile.admin")}</span>}
          <Link
            to="/pricing"
            className={`inline-flex items-center gap-1 text-xs font-medium px-3 py-1 rounded-full ${
              user?.plan === "free"
                ? "bg-gray-100 text-gray-500"
                : user?.plan === "pro"
                ? "bg-sky-100 text-sky-600"
                : "bg-gold-100 text-gold-600"
            }`}
          >
            {user?.plan === "free" ? <Star className="w-3 h-3" /> : <Crown className="w-3 h-3" />}
            {planLabel}
            {user?.plan !== "free" && " \u2713"}
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="card text-center !p-4">
          <p className="text-xl font-bold text-sky-500">{stats.completed_lessons}</p>
          <p className="text-xs text-gray-400">{t("profile.lessons")}</p>
        </div>
        <div className="card text-center !p-4">
          <p className="text-xl font-bold text-gold-500">{stats.badges}</p>
          <p className="text-xs text-gray-400">{t("profile.badges")}</p>
        </div>
        <div className="card text-center !p-4">
          <p className="text-xl font-bold text-orange-500">{stats.savings_goals}</p>
          <p className="text-xs text-gray-400">{t("profile.goals")}</p>
        </div>
      </div>

      <div className="space-y-1">
        {menuItems.map(({ icon: Icon, label, to }) => (
          <Link key={label} to={to} className="card !p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-3">
              <Icon className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">{label}</span>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-300" />
          </Link>
        ))}
      </div>

      <button onClick={logout} className="card !p-4 flex items-center gap-3 w-full hover:bg-rose-50 transition-colors">
        <LogOut className="w-5 h-5 text-rose-400" />
        <span className="text-sm font-medium text-rose-600">{t("profile.signOut")}</span>
      </button>
    </div>
  );
}
