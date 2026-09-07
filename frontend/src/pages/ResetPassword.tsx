import { useEffect, useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Lock, Eye, EyeOff } from "lucide-react";
import client from "../api/client";

export default function ResetPassword() {
  useEffect(() => { document.title = "Reset Password - Finwize"; }, []);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") || "";
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      await client.post("/auth/reset-password", { token, new_password: password });
      toast.success("Password reset successfully. Please login.");
      navigate("/login");
    } catch {
      toast.error("Reset failed. The link may have expired.");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-sky-50 via-white to-gold-50">
        <div className="w-full max-w-sm text-center card space-y-4">
          <h1 className="text-xl font-bold text-gray-800">Invalid reset link</h1>
          <p className="text-sm text-gray-500">This link is missing or invalid. Please request a new one.</p>
          <Link to="/forgot-password" className="btn-primary inline-block w-full text-center">Request Reset</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-sky-50 via-white to-gold-50">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-400 to-sky-600 flex items-center justify-center text-white font-bold text-lg">F</div>
            <span className="font-bold text-2xl text-gray-800">EcoFinwize</span>
          </Link>
          <h1 className="text-2xl font-bold text-gray-800">Reset password</h1>
          <p className="text-gray-500 text-sm mt-1">Enter your new password</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-600 block mb-1.5">New Password</label>
            <div className="relative">
              <input type={showPw ? "text" : "password"} className="input-field pr-10" placeholder="Min. 8 characters" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} />
              <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" onClick={() => setShowPw(!showPw)}>
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            {loading ? <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" /> : <><Lock className="w-4 h-4" /> Reset Password</>}
          </button>
        </form>
      </div>
    </div>
  );
}
