import { lazy, Suspense, type ReactNode } from "react";
import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { GOOGLE_CLIENT_ID, googleAuthEnabled } from "./config/google";
import Layout from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DarkModeProvider } from "./context/DarkModeContext";
import { ErrorBoundary } from "./components/ErrorBoundary";

const Landing = lazy(() => import("./pages/Landing"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Budget = lazy(() => import("./pages/Budget"));
const Transactions = lazy(() => import("./pages/Transactions"));
const Savings = lazy(() => import("./pages/Savings"));
const Advisor = lazy(() => import("./pages/Advisor"));
const Mentor = lazy(() => import("./pages/Mentor"));
const Investment = lazy(() => import("./pages/Investment"));
const Learning = lazy(() => import("./pages/Learning"));
const ArticleDetail = lazy(() => import("./pages/ArticleDetail"));
const Articles = lazy(() => import("./pages/Articles"));
const Blog = lazy(() => import("./pages/Blog"));
const BlogDetail = lazy(() => import("./pages/BlogDetail"));
const News = lazy(() => import("./pages/News"));
const NewsDetail = lazy(() => import("./pages/NewsDetail"));
const Onboarding = lazy(() => import("./pages/Onboarding"));
const VerifyEmail = lazy(() => import("./pages/VerifyEmail"));
const Forum = lazy(() => import("./pages/Forum"));
const BusinessTasks = lazy(() => import("./pages/BusinessTasks"));
const Invoices = lazy(() => import("./pages/Invoices"));
const BusinessPlan = lazy(() => import("./pages/BusinessPlan"));
const Profile = lazy(() => import("./pages/Profile"));
const Pricing = lazy(() => import("./pages/Pricing"));
const Notifications = lazy(() => import("./pages/Notifications"));
const Admin = lazy(() => import("./pages/Admin"));
const PaymentCallback = lazy(() => import("./pages/PaymentCallback"));
const Calculators = lazy(() => import("./pages/Calculators"));

function RouteFallback() {
  return (
    <div
      className="min-h-[60vh] flex items-center justify-center"
      role="status"
      aria-label="Loading"
    >
      <div className="flex items-center gap-3 text-gray-400">
        <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        <span className="text-sm font-medium">Loading EcoFinwize…</span>
      </div>
    </div>
  );
}

const HeavyPageErrorBoundary = ({ children }: { children: ReactNode }) => (
  <ErrorBoundary
    showDetails={import.meta.env.DEV}
    onError={(error) => console.error("Heavy page error:", error)}
  >
    {children}
  </ErrorBoundary>
);

export default function App() {
  const app = (
    <DarkModeProvider>
      <Toaster position="top-center" toastOptions={{ duration: 3000, style: { borderRadius: "12px", padding: "12px 16px", fontSize: "14px" } }} />
      <ErrorBoundary showDetails={import.meta.env.DEV}>
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/onboarding" element={<Onboarding />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/subscriptions/callback" element={<PaymentCallback />} />
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<ProtectedRoute><HeavyPageErrorBoundary><Dashboard /></HeavyPageErrorBoundary></ProtectedRoute>} />
              <Route path="/budget" element={<ProtectedRoute><Budget /></ProtectedRoute>} />
              <Route path="/transactions" element={<ProtectedRoute><Transactions /></ProtectedRoute>} />
              <Route path="/savings" element={<ProtectedRoute><Savings /></ProtectedRoute>} />
              <Route path="/advisor" element={<ProtectedRoute><HeavyPageErrorBoundary><Advisor /></HeavyPageErrorBoundary></ProtectedRoute>} />
              <Route path="/mentor" element={<ProtectedRoute><HeavyPageErrorBoundary><Mentor /></HeavyPageErrorBoundary></ProtectedRoute>} />
              <Route path="/investment" element={<ProtectedRoute><HeavyPageErrorBoundary><Investment /></HeavyPageErrorBoundary></ProtectedRoute>} />
              <Route path="/learning" element={<ProtectedRoute><Learning /></ProtectedRoute>} />
              <Route path="/articles" element={<ProtectedRoute><Articles /></ProtectedRoute>} />
              <Route path="/articles/:id" element={<ProtectedRoute><ArticleDetail /></ProtectedRoute>} />
              <Route path="/blog" element={<ProtectedRoute><Blog /></ProtectedRoute>} />
              <Route path="/blog/:id" element={<ProtectedRoute><BlogDetail /></ProtectedRoute>} />
              <Route path="/news" element={<ProtectedRoute><News /></ProtectedRoute>} />
              <Route path="/news/:id" element={<ProtectedRoute><NewsDetail /></ProtectedRoute>} />
              <Route path="/forum" element={<ProtectedRoute><Forum /></ProtectedRoute>} />
              <Route path="/business" element={<ProtectedRoute><BusinessTasks /></ProtectedRoute>} />
              <Route path="/invoices" element={<ProtectedRoute><Invoices /></ProtectedRoute>} />
              <Route path="/business-plan" element={<ProtectedRoute><BusinessPlan /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/pricing" element={<ProtectedRoute><Pricing /></ProtectedRoute>} />
              <Route path="/calculators" element={<ProtectedRoute><Calculators /></ProtectedRoute>} />
              <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
              <Route path="/admin" element={<ProtectedRoute adminOnly><Admin /></ProtectedRoute>} />
            </Route>
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </DarkModeProvider>
  );

  return googleAuthEnabled ? (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>{app}</GoogleOAuthProvider>
  ) : (
    app
  );
}