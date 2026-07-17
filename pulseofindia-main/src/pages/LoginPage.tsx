import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Eye, EyeOff, LogIn, AlertCircle, CheckCircle } from "lucide-react";
import { apiLogin, saveUser, saveProfile, apiGetMe } from "../lib/api";

const LoginPage = () => {
  const navigate = useNavigate();
  const [showPw, setShowPw]     = useState(false);
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [success, setSuccess]   = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Step 1: Get JWT token
      const tokenData = await apiLogin(email, password);
      saveUser(tokenData);

      // Step 2: Fetch user profile
      try {
        const profile = await apiGetMe();
        saveProfile(profile);
      } catch {
        // Non-fatal — token still works
      }

      setSuccess(true);
      setTimeout(() => navigate("/election-pulse"), 1000);
    } catch (err: any) {
      setError(err.message || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-primary/20 flex items-center justify-center mx-auto mb-4">
            <Shield className="h-7 w-7 text-primary" />
          </div>
          <h1 className="font-display text-2xl font-bold">Welcome Back</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Login to cast your civic vote
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card-glass p-8 space-y-4">
          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 text-red-400 text-sm p-3 bg-red-500/10 rounded-lg border border-red-500/20">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Success */}
          {success && (
            <div className="flex items-center gap-2 text-green-400 text-sm p-3 bg-green-500/10 rounded-lg border border-green-500/20">
              <CheckCircle className="h-4 w-4 shrink-0" />
              <span>Login successful! Redirecting…</span>
            </div>
          )}

          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-muted/30 border border-border rounded-lg p-3 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm transition-all"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Password</label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-muted/30 border border-border rounded-lg p-3 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm transition-all"
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              >
                {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-saffron w-full py-3.5 rounded-xl text-sm flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                Logging in…
              </>
            ) : (
              <>
                <LogIn className="h-4 w-4" />
                Login
              </>
            )}
          </button>

          <p className="text-center text-xs text-muted-foreground pt-1">
            Don't have an account?{" "}
            <button
              type="button"
              onClick={() => navigate("/signup")}
              className="text-primary hover:underline font-medium"
            >
              Sign Up — it's free
            </button>
          </p>
        </form>
      </motion.div>
    </div>
  );
};

export default LoginPage;
