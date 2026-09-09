import { useEffect, useState } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { CheckCircle, XCircle, Mail } from "lucide-react";
import client from "../api/client";

type Status = "loading" | "success" | "error";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<Status>("loading");
  const [resending, setResending] = useState(false);
  const token = searchParams.get("token");

  useEffect(() => {
    document.title = "Verify Email - EcoFinwize";
    if (!token) { setStatus("error"); return; }
    client.post("/auth/verify-email", { token })
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [token]);

  const handleResend = async () => {
    const email = prompt("Enter your email address:");
    if (!email) return;
    setResending(true);
    try {
      await client.post("/auth/resend-verification", { email });
      alert("Verification email sent if account exists.");
    } catch {
      alert("Failed to resend. Please try again.");
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-sky-50 via-white to-gold-50">
      <div className="w-full max-w-sm card text-center space-y-4">
        {status === "loading" && (
          <>
            <div className="w-16 h-16 rounded-full bg-sky-50 flex items-center justify-center mx-auto">
              <div className="w-8 h-8 border-4 border-sky-200 border-t-sky-500 rounded-full animate-spin" />
            </div>
            <h1 className="text-xl font-bold text-gray-800">Verifying your email...</h1>
          </>
        )}
        {status === "success" && (
          <>
            <div className="w-16 h-16 rounded-full bg-green-50 flex items-center justify-center mx-auto">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <h1 className="text-xl font-bold text-gray-800">Email verified!</h1>
            <p className="text-sm text-gray-500">Your email has been successfully verified.</p>
            <button onClick={() => navigate("/dashboard")} className="btn-primary w-full">Go to Dashboard</button>
          </>
        )}
        {status === "error" && (
          <>
            <div className="w-16 h-16 rounded-full bg-rose-50 flex items-center justify-center mx-auto">
              <XCircle className="w-8 h-8 text-rose-500" />
            </div>
            <h1 className="text-xl font-bold text-gray-800">Verification failed</h1>
            <p className="text-sm text-gray-500">The verification link is invalid or expired.</p>
            <button onClick={handleResend} disabled={resending} className="btn-primary w-full">
              {resending ? "Sending..." : "Resend Verification Email"}
            </button>
            <Link to="/login" className="block text-sm text-sky-500 hover:underline">Back to Login</Link>
          </>
        )}
      </div>
    </div>
  );
}
