import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Eye, EyeOff, UserPlus, AlertCircle, CheckCircle, Wifi, WifiOff } from "lucide-react";
import { apiSignup, wakeBackend } from "../lib/api";

const STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
  "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
  "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
  "West Bengal",
  // Union Territories
  "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry",
  "Chandigarh", "Dadra & Nagar Haveli", "Daman & Diu", "Lakshadweep",
  "Andaman & Nicobar Islands",
];

const AGE_OPTIONS: { label: string; value: string }[] = [
  { label: "18 – 25",  value: "18-25"  },
  { label: "26 – 40",  value: "26-40"  },
  { label: "41 – 60",  value: "41-60"  },
  { label: "60+",      value: "60+"    },
];

const SignUpPage = () => {
  const navigate = useNavigate();
  const [showPw, setShowPw]               = useState(false);
  const [fullName, setFullName]           = useState("");
  const [email, setEmail]                 = useState("");
  const [password, setPassword]           = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [ageGroup, setAgeGroup]           = useState("");
  const [state, setState]                 = useState("");
  const [agree, setAgree]                 = useState(false);
  const [loading, setLoading]             = useState(false);
  const [error, setError]                 = useState<string | null>(null);
  const [success, setSuccess]             = useState(false);
  const [backendReady, setBackendReady]   = useState<boolean | null>(null); // null=checking

  // Wake the backend as soon as this page loads so it's ready when user submits
  useEffect(() => {
    setBackendReady(null);
    wakeBackend().then((ok) => setBackendReady(ok));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!fullName.trim())        return setError("Full name is required.");
    if (!email.trim())           return setError("Email is required.");
    if (password.length < 6)     return setError("Password must be at least 6 characters.");
    if (password !== confirmPassword) return setError("Passwords do not match.");
    if (!ageGroup)               return setError("Please select your age group.");
    if (!state)                  return setError("Please select your state.");
    if (!agree)                  return setError("Please agree to the civic participation disclaimer.");

    setLoading(true);
    try {
      await apiSignup({ full_name: fullName, email, password, age_group: ageGroup, state });
      setSuccess(true);
      setTimeout(() => navigate("/login"), 1500);
    } catch (err: any) {
      const msg = (err.message || "").toLowerCase();
      if (msg.includes("failed to fetch") || msg.includes("network") || msg.includes("load")) {
        setError("Server is still waking up. Please wait a few more seconds and try again.");
        // Retry wakeup check
        setBackendReady(null);
        wakeBackend().then((ok) => setBackendReady(ok));
      } else {
        setError(err.message || "Signup failed. Try a different email.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16">
      {/* Backend wakeup status banner */}
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
              <line x1="32" y1="26.5" x2="32" y2="28.5" stroke="#1e3a8a" strokeWidth="0.8"/>
              <line x1="32" y1="33.5" x2="32" y2="35.5" stroke="#1e3a8a" strokeWidth="0.8"/>
              <line x1="26.5" y1="31" x2="28.5" y2="31" stroke="#1e3a8a" strokeWidth="0.8"/>
              <line x1="35.5" y1="31" x2="37.5" y2="31" stroke="#1e3a8a" strokeWidth="0.8"/>
            </svg>
          </div>
          <h1 className="font-display text-2xl font-bold">Create Civic Account</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Join the movement for transparency &amp; accountability
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
              <span>Account created! Redirecting to login…</span>
            </div>
          )}

          {/* Full Name */}
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Full Name</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-muted/30 border border-border rounded-lg p-3 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
              placeholder="Enter your full name"
            />
          </div>

          {/* Email */}
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-muted/30 border border-border rounded-lg p-3 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
              placeholder="you@example.com"
            />
          </div>

          {/* Password */}
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Password</label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-muted/30 border border-border rounded-lg p-3 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
                placeholder="Min. 6 characters"
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full bg-muted/30 border border-border rounded-lg p-3 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
              placeholder="Re-enter password"
            />
          </div>

          {/* Age Group */}
          <div>
            <label className="text-sm text-muted-foreground mb-2 block">
              Age Group <span className="text-primary">*</span>
              <span className="ml-2 text-xs text-muted-foreground/60">(used to compute age-wise vote statistics)</span>
            </label>
            <div className="grid grid-cols-4 gap-2">
              {AGE_OPTIONS.map((ag) => (
                <button
                  key={ag.value}
                  type="button"
                  onClick={() => setAgeGroup(ag.value)}
                  className={`p-2.5 rounded-lg border text-sm font-medium transition-all ${
                    ageGroup === ag.value
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted-foreground hover:border-muted-foreground/50"
                  }`}
                >
                  {ag.label}
                </button>
              ))}
            </div>
          </div>

          {/* State */}
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">
              State / UT <span className="text-primary">*</span>
              <span className="ml-2 text-xs text-muted-foreground/60">(for state-wise results)</span>
            </label>
            <select
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="w-full bg-muted/30 border border-border rounded-lg p-3 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
            >
              <option value="">Select your state or UT…</option>
              <optgroup label="States">
                {STATES.filter(s => !["Delhi","Jammu & Kashmir","Ladakh","Puducherry","Chandigarh","Dadra & Nagar Haveli","Daman & Diu","Lakshadweep","Andaman & Nicobar Islands"].includes(s)).map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </optgroup>
              <optgroup label="Union Territories">
                {["Delhi","Jammu & Kashmir","Ladakh","Puducherry","Chandigarh","Dadra & Nagar Haveli","Daman & Diu","Lakshadweep","Andaman & Nicobar Islands"].map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </optgroup>
            </select>
          </div>

          {/* Agree */}
          <label className="flex items-start gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={agree}
              onChange={(e) => setAgree(e.target.checked)}
              className="mt-1 accent-primary"
            />
            <span className="text-xs text-muted-foreground leading-relaxed">
              I agree to the civic participation disclaimer. I understand this is a research platform
              using AI-generated analysis. My vote is anonymous and used only for statistical purposes.
            </span>
          </label>

          <button
            type="submit"
            disabled={loading}
            className="btn-saffron w-full mt-2 py-3.5 rounded-xl text-sm flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                Creating account…
              </>
            ) : (
              <>
                <UserPlus className="h-4 w-4" />
                Create Civic Account
              </>
            )}
          </button>

          <p className="text-center text-xs text-muted-foreground">
            Already have an account?{" "}
            <button
              type="button"
              onClick={() => navigate("/login")}
              className="text-primary hover:underline font-medium"
            >
              Login
            </button>
          </p>
        </form>
      </motion.div>
    </div>
  );
};

export default SignUpPage;
