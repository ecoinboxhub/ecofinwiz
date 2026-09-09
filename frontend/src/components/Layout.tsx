import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Sparkles, Briefcase, LayoutDashboard, BookOpen, Wallet, TrendingUp, Globe, Sun, Moon, Calculator } from "lucide-react";
import AdBanner from "./AdBanner";
import OfflineBanner from "./OfflineBanner";
import { useLanguage, AFRICAN_LANGUAGES, type Language } from "../context/LanguageContext";
import { useDarkMode } from "../context/DarkModeContext";
import { useTranslations } from "../i18n/useTranslations";

const ROUTE_TITLES: Record<string, string> = {
  "/advisor": "Kemi - AI Financial Advisor",
  "/mentor": "Chidi - AI Business Mentor",
  "/investment": "Musa - AI Investment Advisor",
  "/dashboard": "Dashboard",
  "/budget": "Budget",
  "/transactions": "Transactions",
  "/savings": "Savings Goals",
  "/learning": "Learning Hub",
  "/articles": "Articles",
  "/blog": "Blog",
  "/news": "News",
  "/forum": "Forum",
  "/business": "Business Tasks",
  "/invoices": "Invoices",
  "/business-plan": "Business Plan",
  "/profile": "Profile",
  "/pricing": "Pricing",
  "/calculators": "Calculators",
  "/notifications": "Notifications",
  "/admin": "Admin Dashboard",
};

export default function Layout() {
  const location = useLocation();
  const hideNav = ["/login", "/register", "/"].includes(location.pathname);
  const { language, setLanguage } = useLanguage();
  const { dark, toggle: toggleDark } = useDarkMode();
  const [showLangPicker, setShowLangPicker] = useState(false);
  const { t } = useTranslations();

  useEffect(() => {
    const base = Object.keys(ROUTE_TITLES).find((k) => location.pathname.startsWith(k));
    document.title = base ? `${ROUTE_TITLES[base]} - EcoFinwize` : "EcoFinwize";
  }, [location.pathname]);

  const navItems = [
    { to: "/advisor", icon: Sparkles, label: t("nav.kemi") },
    { to: "/mentor", icon: Briefcase, label: t("nav.chidi") },
    { to: "/dashboard", icon: LayoutDashboard, label: t("nav.home") },
    { to: "/calculators", icon: Calculator, label: "Calculators" },
    { to: "/learning", icon: BookOpen, label: t("nav.learn") },
    { to: "/investment", icon: TrendingUp, label: t("nav.musa") },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      <OfflineBanner />
      <a href="#main-content" className="skip-link">{t("layout.skipToContent") || "Skip to content"}</a>
      {!hideNav && (
        <header className="sticky top-0 z-40 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-100 dark:border-gray-700 px-4 py-3 pt-safe flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-sky-600 flex items-center justify-center text-white font-bold text-sm">F</div>
            <span className="font-bold text-lg text-gray-800 dark:text-gray-100">{t("layout.finwize")}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleDark}
              className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {dark ? <Sun className="w-4 h-4 text-gray-400" /> : <Moon className="w-4 h-4 text-gray-500" />}
            </button>
            <button
              onClick={() => setShowLangPicker(!showLangPicker)}
              className="flex items-center gap-1 p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-xs font-medium text-gray-600 dark:text-gray-300"
              title={t("layout.selectLanguage")}
              aria-label={t("layout.selectLanguage")}
            >
              <Globe className="w-4 h-4" />
              <span className="hidden sm:inline">{language.nativeName}</span>
            </button>
            <NavLink to="/notifications" className="relative p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors" aria-label="Notifications">
              <svg className="w-5 h-5 text-gray-500 dark:text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
              <span className="absolute top-1 right-1 w-2 h-2 bg-rose-500 rounded-full" />
            </NavLink>
            <NavLink to="/profile" className="w-8 h-8 rounded-full bg-sky-100 dark:bg-sky-900/50 flex items-center justify-center text-sky-600 dark:text-sky-400 font-semibold text-sm" aria-label="Profile">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </NavLink>
          </div>
        </header>
      )}

      {showLangPicker && !hideNav && (
        <div className="fixed top-14 right-4 z-50 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-3 max-h-80 overflow-y-auto w-56" role="dialog" aria-label={t("layout.selectLanguage")}>
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-2 mb-2">{t("layout.selectLanguage")}</p>
          {AFRICAN_LANGUAGES.map(lang => (
            <button
              key={lang.code}
              onClick={() => { setLanguage(lang); setShowLangPicker(false); }}
              className={`w-full text-left px-3 py-2 rounded-xl text-sm transition-colors ${language.code === lang.code ? "bg-sky-50 dark:bg-sky-900/40 text-sky-600 dark:text-sky-400 font-medium" : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"}`}
            >
              <span>{lang.name}</span>
              <span className="text-gray-400 ml-1 text-xs">({lang.nativeName})</span>
            </button>
          ))}
        </div>
      )}

      <main id="main-content" className={`flex-1 ${!hideNav ? "pb-20" : ""}`}>
        <AdBanner pageContext={location.pathname.split("/")[1] || "advisor"} />
        <Outlet />
      </main>

      {!hideNav && (
        <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white/90 dark:bg-gray-800/90 backdrop-blur-lg border-t border-gray-100 dark:border-gray-700 px-2 pb-safe" aria-label="Main navigation">
          <div className="flex justify-around py-2">
            {navItems.map(({ to, icon: Icon, label }) => {
              const isActive = location.pathname.startsWith(to);
              return (
                <NavLink key={to} to={to} className={`nav-link ${isActive ? "active" : ""}`} aria-current={isActive ? "page" : undefined}>
                  <Icon className="w-5 h-5" />
                  <span>{label}</span>
                </NavLink>
              );
            })}
          </div>
        </nav>
      )}
    </div>
  );
}
