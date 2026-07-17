import { Link, useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { Menu, X, LogIn, UserPlus, LogOut, User, ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { isLoggedIn, getProfile, clearUser } from "../lib/api";


const navItems = [
  { label: "Dashboard", path: "/" },
  { label: "Analyzer", path: "/analyzer" },
  { label: "Public Pulse", path: "/public-pulse" },
  { label: "Election Pulse", path: "/election-pulse" },
  { label: "Trending", path: "/trending" },
  { label: "Leaders", path: "/leaders" },
];

const Navbar = () => {
  const location  = useLocation();
  const navigate  = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [loggedIn, setLoggedIn]     = useState(false);
  const [profile, setProfile]       = useState<Record<string, unknown> | null>(null);
  const [dropOpen, setDropOpen]     = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);

  // Re-check auth state on every route change
  useEffect(() => {
    setLoggedIn(isLoggedIn());
    setProfile(getProfile());
  }, [location.pathname]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropRef.current && !dropRef.current.contains(e.target as Node)) {
        setDropOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleLogout = () => {
    clearUser();
    setLoggedIn(false);
    setProfile(null);
    setDropOpen(false);
    navigate("/login");
  };

  // Get initials from profile name
  const initials = (() => {
    const name = (profile?.full_name as string) || "";
    return name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase() || "U";
  })();

  const displayName = (profile?.full_name as string) || "User";
  const displayState = (profile?.state as string) || "";

  return (
    <nav className="nav-glass fixed top-0 left-0 right-0 z-50">
      <div className="container mx-auto flex items-center justify-between h-16 px-4">
        <Link to="/" className="flex items-center gap-2.5">
          {/* Indian tricolor emblem */}
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
            <line x1="27.9" y1="27.9" x2="29.3" y2="29.3" stroke="#1e3a8a" strokeWidth="0.8"/>
            <line x1="34.7" y1="32.7" x2="36.1" y2="34.1" stroke="#1e3a8a" strokeWidth="0.8"/>
            <line x1="36.1" y1="27.9" x2="34.7" y2="29.3" stroke="#1e3a8a" strokeWidth="0.8"/>
            <line x1="29.3" y1="32.7" x2="27.9" y2="34.1" stroke="#1e3a8a" strokeWidth="0.8"/>
          </svg>
          <span className="font-display font-bold text-lg text-foreground">
            Bharat <span className="text-gradient-saffron">Truth Lens</span>
          </span>
        </Link>

        {/* Desktop nav links */}
        <div className="hidden lg:flex items-center gap-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location.pathname === item.path
                  ? "text-primary bg-primary/10"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>

        {/* Desktop auth section */}
        <div className="hidden lg:flex items-center gap-3">
          {loggedIn ? (
            <div className="relative" ref={dropRef}>
              <button
                onClick={() => setDropOpen(!dropOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 hover:bg-primary/20 transition-all"
              >
                {/* Avatar */}
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-orange-500 to-green-500 flex items-center justify-center text-xs font-bold text-white">
                  {initials}
                </div>
                <div className="text-left">
                  <div className="text-sm font-medium text-foreground leading-none">{displayName}</div>
                  {displayState && <div className="text-xs text-muted-foreground leading-none mt-0.5">{displayState}</div>}
                </div>
                <ChevronDown className={`h-3.5 w-3.5 text-muted-foreground transition-transform ${dropOpen ? "rotate-180" : ""}`} />
              </button>

              <AnimatePresence>
                {dropOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -8, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -8, scale: 0.95 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 mt-2 w-48 bg-card border border-border rounded-xl shadow-xl overflow-hidden"
                  >
                    <div className="px-4 py-3 border-b border-border/50">
                      <div className="text-sm font-semibold text-foreground">{displayName}</div>
                      <div className="text-xs text-muted-foreground">{displayState}</div>
                    </div>
                    <Link
                      to="/election-pulse"
                      onClick={() => setDropOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-foreground hover:bg-muted/50 transition-colors"
                    >
                      <User className="h-4 w-4 text-primary" /> My Votes
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                    >
                      <LogOut className="h-4 w-4" /> Logout
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <>
              <Link
                to="/login"
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                <LogIn className="h-4 w-4" /> Login
              </Link>
              <Link
                to="/signup"
                className="btn-saffron text-sm flex items-center gap-1.5"
              >
                <UserPlus className="h-4 w-4" /> Sign Up
              </Link>
            </>
          )}
        </div>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="lg:hidden text-foreground p-2"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden border-t border-border/50 bg-card/95 backdrop-blur-xl"
          >
            <div className="px-4 py-4 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileOpen(false)}
                  className={`block px-3 py-2 rounded-md text-sm font-medium ${
                    location.pathname === item.path
                      ? "text-primary bg-primary/10"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {item.label}
                </Link>
              ))}

              <div className="pt-3 border-t border-border/50">
                {loggedIn ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-3 px-3 py-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-green-500 flex items-center justify-center text-sm font-bold text-white">
                        {initials}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-foreground">{displayName}</div>
                        <div className="text-xs text-muted-foreground">{displayState}</div>
                      </div>
                    </div>
                    <button
                      onClick={() => { handleLogout(); setMobileOpen(false); }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 rounded-md transition-colors"
                    >
                      <LogOut className="h-4 w-4" /> Logout
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <Link to="/login" onClick={() => setMobileOpen(false)} className="flex-1 text-center px-3 py-2 text-sm text-muted-foreground border border-border rounded-md">
                      Login
                    </Link>
                    <Link to="/signup" onClick={() => setMobileOpen(false)} className="flex-1 text-center btn-saffron text-sm rounded-md">
                      Sign Up
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
