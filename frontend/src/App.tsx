import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { GOOGLE_CLIENT_ID, googleAuthEnabled } from "./config/google";
import Layout from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DarkModeProvider } from "./context/DarkModeContext";
import { ErrorBoundary } from "./components/ErrorBoundary";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import Budget from "./pages/Budget";
import Transactions from "./pages/Transactions";
import Savings from "./pages/Savings";
import Advisor from "./pages/Advisor";
import Mentor from "./pages/Mentor";
import Investment from "./pages/Investment";
import Learning from "./pages/Learning";
import ArticleDetail from "./pages/ArticleDetail";
import Articles from "./pages/Articles";
import Blog from "./pages/Blog";
import BlogDetail from "./pages/BlogDetail";
import News from "./pages/News";
import NewsDetail from "./pages/NewsDetail";
import Onboarding from "./pages/Onboarding";
import VerifyEmail from "./pages/VerifyEmail";
import Forum from "./pages/Forum";
import BusinessTasks from "./pages/BusinessTasks";
import Invoices from "./pages/Invoices";
import BusinessPlan from "./pages/BusinessPlan";
import Profile from "./pages/Profile";
import Pricing from "./pages/Pricing";
import Notifications from "./pages/Notifications";
import Admin from "./pages/Admin";
import PaymentCallback from "./pages/PaymentCallback";
import Calculators from "./pages/Calculators";

const HeavyPageErrorBoundary = ({ children }: { children: React.ReactNode }) => (
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
      </ErrorBoundary>
      </DarkModeProvider>
  );

  return googleAuthEnabled ? (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>{app}</GoogleOAuthProvider>
  ) : (
    app
  );
}
