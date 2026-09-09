import { useEffect } from "react";
import { Link } from "react-router-dom";
import { TrendingUp, Shield, BookOpen, Wallet, Sparkles, ArrowRight, Star, Users, Globe, MessageCircle, Download } from "lucide-react";
import { useTranslations } from "../i18n/useTranslations";

export default function Landing() {
  const { t } = useTranslations();
  useEffect(() => { document.title = "EcoFinwize - AI-Powered Financial & Business Guidance"; }, []);

  const features = [
    { icon: MessageCircle, title: t("landing.feature1Title"), desc: t("landing.feature1Desc"), color: "text-sky-500 bg-sky-50" },
    { icon: TrendingUp, title: t("landing.feature2Title"), desc: t("landing.feature2Desc"), color: "text-gold-500 bg-gold-50" },
    { icon: BookOpen, title: t("landing.feature3Title"), desc: t("landing.feature3Desc"), color: "text-orange-500 bg-orange-50" },
    { icon: Shield, title: t("landing.feature4Title"), desc: t("landing.feature4Desc"), color: "text-rose-500 bg-rose-50" },
    { icon: Wallet, title: t("landing.feature5Title"), desc: t("landing.feature5Desc"), color: "text-sky-500 bg-sky-50" },
    { icon: Sparkles, title: t("landing.feature6Title"), desc: t("landing.feature6Desc"), color: "text-gold-500 bg-gold-50" },
  ];

  const stats = [
    { icon: Users, value: "10K+", label: t("landing.activeUsers") },
    { icon: Star, value: "4.8", label: t("landing.appRating") },
    { icon: Globe, value: "15+", label: t("landing.countries") },
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <header className="px-4 py-4 pt-safe flex items-center justify-between max-w-6xl mx-auto w-full">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-sky-600 flex items-center justify-center text-white font-bold text-sm">F</div>
          <span className="font-bold text-xl text-gray-800 dark:text-gray-100">{t("layout.finwize")}</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-gray-600 dark:text-gray-400 font-medium hover:text-sky-600 dark:hover:text-sky-400 transition-colors">{t("landing.login")}</Link>
          <Link to="/register" className="btn-primary text-sm !px-4 !py-2">{t("landing.getStarted")}</Link>
        </div>
      </header>
 
      <section className="px-4 pt-16 pb-20 text-center max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-sky-50 dark:bg-sky-900/40 text-sky-600 dark:text-sky-400 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
          <Sparkles className="w-4 h-4" /> {t("landing.heroBadge")}
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 dark:text-gray-100 leading-tight mb-6">
          {t("landing.heroYour")}{" "}
          <span className="bg-gradient-to-r from-sky-500 via-gold-400 to-orange-500 bg-clip-text text-transparent">
            {t("landing.heroFinancial")}
          </span>
          {t("landing.heroPowered")}
        </h1>
        <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto mb-8">
          {t("landing.heroDesc")}
        </p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link to="/register" className="btn-primary text-lg !px-8 !py-3 flex items-center gap-2">
            {t("landing.startFree")} <ArrowRight className="w-5 h-5" />
          </Link>
          <Link to="/login" className="btn-secondary text-lg !px-8 !py-3">{t("landing.watchDemo")}</Link>
          <a href="/downloads/ecofinwiz.apk" download className="btn-secondary text-lg !px-8 !py-3 flex items-center gap-2">
            <Download className="w-5 h-5" /> {t("landing.downloadApk")}
          </a>
        </div>
        <div className="flex items-center justify-center gap-8 mt-10">
          {stats.map(({ icon: Icon, value, label }) => (
            <div key={label} className="text-center">
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-100">{value}</div>
              <div className="text-sm text-gray-400 dark:text-gray-500 flex items-center gap-1 justify-center"><Icon className="w-3.5 h-3.5" />{label}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="px-4 py-16 bg-gray-50 dark:bg-gray-800/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-center text-gray-800 dark:text-gray-100 mb-12">{t("landing.sectionTitle")}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className="card hover:shadow-md transition-shadow">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-2">{title}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 py-16 max-w-6xl mx-auto text-center">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-gray-100 mb-4">{t("landing.ctaTitle")}</h2>
        <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-xl mx-auto">{t("landing.ctaDesc")}</p>
        <Link to="/register" className="btn-primary text-lg !px-10 !py-3">{t("landing.createFree")}</Link>
      </section>

      <footer className="px-4 py-8 border-t border-gray-100 dark:border-gray-700 text-center text-sm text-gray-400 dark:text-gray-500">
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-sky-400 to-sky-600 flex items-center justify-center text-white font-bold text-xs">F</div>
          <span className="font-semibold text-gray-600 dark:text-gray-400">{t("layout.finwize")}</span>
        </div>
        <div className="mb-2"><a href="/downloads/ecofinwiz.apk" download className="inline-flex items-center gap-1 text-sky-500 font-medium hover:underline"><Download className="w-3.5 h-3.5" /> {t("landing.downloadApk")}</a></div>
        {t("landing.copyright")}
      </footer>
    </div>
  );
}
