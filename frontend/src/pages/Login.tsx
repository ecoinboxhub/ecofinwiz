import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { GoogleLogin } from "@react-oauth/google";
import { LogIn, Eye, EyeOff } from "lucide-react";
import { useTranslations } from "../i18n/useTranslations";
import client from "../api/client";
import { googleAuthVisible } from "../config/google";

export default function Login() {
  useEffect(() => { document.title = "Login - EcoFinwize"; }, []);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, googleLogin } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslations();

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setError("");
    try {
      await googleLogin(credentialResponse.credential);
      navigate("/advisor");
    } catch (err: any) {
      setError(err.response?.data?.detail || t("login.googleFailed"));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      const token = localStorage.getItem("access_token");
      if (token) {
        const { data: profile } = await client.get("/users/me").catch(() => ({ data: null }));
        if (profile && !profile.onboarding_completed) { navigate("/onboarding"); return; }
      }
      navigate("/advisor");
    } catch (err: any) {
      setError(err.response?.data?.detail || t("login.invalidCredentials"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-sky-50 dark:from-gray-900 via-white dark:via-gray-800 to-gold-50 dark:to-gray-900">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-400 to-sky-600 flex items-center justify-center text-white font-bold text-lg">F</div>
            <span className="font-bold text-2xl text-gray-800 dark:text-gray-100">{t("layout.finwize")}</span>
          </Link>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{t("login.welcomeBack")}</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">{t("login.signIn")}</p>
        </div>
 
        <form onSubmit={handleSubmit} className="card space-y-4">
          {error && <div className="bg-rose-50 dark:bg-rose-900/40 text-rose-600 dark:text-rose-400 text-sm px-4 py-2.5 rounded-xl" id="login-error" role="alert">{error}</div>}
 
          <div>
            <label className="text-sm font-medium text-gray-600 dark:text-gray-400 block mb-1.5" htmlFor="login-email">{t("login.email")}</label>
            <input id="login-email" type="email" className="input-field" placeholder={t("login.emailPlaceholder")} value={email} onChange={e => setEmail(e.target.value)} required aria-describedby={error ? "login-error" : undefined} />
          </div>
 
          <div>
            <label className="text-sm font-medium text-gray-600 dark:text-gray-400 block mb-1.5" htmlFor="login-password">{t("login.password")}</label>
            <div className="relative">
              <input id="login-password" type={showPw ? "text" : "password"} className="input-field pr-10" placeholder={t("login.passwordPlaceholder")} value={password} onChange={e => setPassword(e.target.value)} required aria-describedby={error ? "login-error" : undefined} />
              <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" aria-label={showPw ? "Hide password" : "Show password"} onClick={() => setShowPw(!showPw)}>
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            {loading ? <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" /> : <><LogIn className="w-4 h-4" /> {t("login.signInBtn")}</>}
          </button>

          <div className="text-right">
            <Link to="/forgot-password" className="text-xs text-sky-500 hover:underline">Forgot password?</Link>
          </div>

          {googleAuthVisible && (
          <>
          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-200 dark:border-gray-600" /></div>
            <div className="relative flex justify-center"><span className="bg-white dark:bg-gray-800 px-3 text-sm text-gray-400 dark:text-gray-500">{t("login.or")}</span></div>
          </div>

          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError(t("login.googleFailed"))}
              useOneTap
            />
          </div>
          </>
          )}

          <p className="text-center text-sm text-gray-500 dark:text-gray-400 pt-2">
            {t("login.noAccount")} <Link to="/register" className="text-sky-500 font-medium hover:underline">{t("login.signUp")}</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
