import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Eye, EyeOff, LogIn, AlertCircle, CheckCircle, Wifi, WifiOff } from "lucide-react";
import { apiLogin, saveUser, saveProfile, apiGetMe, wakeBackend } from "../lib/api";

const LoginPage = () => {
  const navigate = useNavigate();
  const [showPw, setShowPw]     = useState(false);
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [success, setSuccess]   = useState(false);
  const [backendReady, setBackendReady] = useState<boolean | null>(null);

  useEffect(() => {
    wakeBackend().then((ok) => setBackendReady(ok));
  }, []);

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
      {backendReady === null && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-yellow-500/20 border border-yellow-500/40 text-yellow-300 text-sm px-4 py-2 rounded-full backdrop-blur-sm">
          <div className="animate-spin h-3.5 w-3.5 border-2 border-yellow-400 border-t-transparent rounded-full" />
          Connecting to server… (may take up to 60s on free tier)
        </div>
      )}
      {backendReady === true && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-green-500/20 border border-green-500/40 text-green-300 text-sm px-4 py-2 rounded-full backdrop-blur-sm">
          <Wifi className="h-3.5 w-3.5" /> Server ready
        </div>
      )}
      {backendReady === false && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-red-500/20 border border-red-500/40 text-red-300 text-sm px-4 py-2 rounded-full backdrop-blur-sm">
          <WifiOff className="h-3.5 w-3.5" /> Server unreachable — try refreshing
        </div>
      )}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-primary/20 flex items-center justify-center mx-auto mb-4">
            <svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="32" cy="32" r="30" fill="#0F172A" stroke="#FF6B35" strokeWidth="2"/>
              <rect x="10" y="19" width="44" height="8" rx="1" fill="#FF6B35"/>
              <rect x="10" y="27" width="44" height="8" rx="1" fill="#F8FAFC"/>
              <rect x="10" y="35" width="44" height="8" rx="1" fill="#22C55E"/>
              <circle cx="32" cy="31" r="5" fill="none" stroke="#1e3a8a" strokeWidth="1.5"/>
              <circle cx="32" cy="31" r="1.5" fill="#1e3a8a"/>
            </svg>
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
