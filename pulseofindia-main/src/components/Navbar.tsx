import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { Menu, X, LogIn, UserPlus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";


const navItems = [
  { label: "Dashboard", path: "/" },
  { label: "Analyzer", path: "/analyzer" },
  { label: "Public Pulse", path: "/public-pulse" },
  { label: "Election Pulse", path: "/election-pulse" },
  { label: "Trending", path: "/trending" },
  { label: "Leaders", path: "/leaders" },
];

const Navbar = () => {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

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


        {/* Desktop nav */}
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

        <div className="hidden lg:flex items-center gap-3">
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
              <div className="pt-3 border-t border-border/50 flex gap-2">
                <Link to="/login" onClick={() => setMobileOpen(false)} className="flex-1 text-center px-3 py-2 text-sm text-muted-foreground border border-border rounded-md">
                  Login
                </Link>
                <Link to="/signup" onClick={() => setMobileOpen(false)} className="flex-1 text-center btn-saffron text-sm rounded-md">
                  Sign Up
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
