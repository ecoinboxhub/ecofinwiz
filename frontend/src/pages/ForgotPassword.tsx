import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { Mail } from "lucide-react";
import client from "../api/client";

export default function ForgotPassword() {
  useEffect(() => { document.title = "Forgot Password - EcoFinwize"; }, []);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post("/auth/forgot-password", { email });
      setSent(true);
      toast.success("Reset link sent if email exists");
    } catch {
      toast.success("Reset link sent if email exists");
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-sky-50 via-white to-gold-50">
        <div className="w-full max-w-sm text-center card space-y-4">
          <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto">
            <Mail className="w-6 h-6 text-green-600" />
          </div>
          <h1 className="text-xl font-bold text-gray-800">Check your email</h1>
          <p className="text-sm text-gray-500">If an account exists with that email, we've sent a password reset link.</p>
          <Link to="/login" className="btn-primary inline-block w-full text-center">Back to Login</Link>
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
          <h1 className="text-2xl font-bold text-gray-800">Forgot password?</h1>
          <p className="text-gray-500 text-sm mt-1">Enter your email and we'll send a reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-600 block mb-1.5">Email</label>
            <input type="email" className="input-field" placeholder="you@example.com" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            {loading ? <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" /> : <><Mail className="w-4 h-4" /> Send Reset Link</>}
          </button>
          <p className="text-center text-sm text-gray-500">
            <Link to="/login" className="text-sky-500 font-medium hover:underline">Back to Login</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
