import { motion } from "framer-motion";
import { Search, ArrowRight, Activity, ShieldAlert, Users, TrendingUp, AlertTriangle } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AnimatedCounter from "../components/AnimatedCounter";
import heroBg from "@/assets/hero-bg.jpg";

const metrics = [
  { label: "National Severity Index", value: 7.4, suffix: "/10", icon: Activity, color: "text-primary" },
  { label: "Fake News Risk", value: 34.2, suffix: "%", icon: ShieldAlert, color: "text-destructive" },
  { label: "Youth Political Engagement", value: 62.8, suffix: "%", icon: Users, color: "text-electric" },
  { label: "Top Trending Case", value: 0, suffix: "", icon: TrendingUp, color: "text-primary", text: "Electoral Bond Probe" },
  { label: "Media Attention Drop", value: 67, suffix: "%", icon: AlertTriangle, color: "text-warning" },
];

const Index = () => {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleAnalyze = () => {
    if (query.trim()) navigate(`/analyzer?q=${encodeURIComponent(query)}`);
    else navigate("/analyzer");
  };

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          <img src={heroBg} alt="" className="w-full h-full object-cover opacity-30" />
          <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/80 to-background" />
        </div>

        <div className="relative z-10 container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <h1 className="font-display text-5xl md:text-7xl font-bold mb-4 tracking-tight">
              Truth. <span className="text-gradient-saffron">Transparency.</span>{" "}
              <span className="text-gradient-electric">Accountability.</span>
            </h1>
            <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto mb-10">
              Understand what's real, what matters, and what your generation thinks.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="max-w-2xl mx-auto"
          >
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
                placeholder="Verify a claim, check old headline updates, or analyze political issues…"
                className="w-full pl-12 pr-36 py-4 bg-card/80 backdrop-blur-xl border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
              />
              <button
                onClick={handleAnalyze}
                className="absolute right-2 top-1/2 -translate-y-1/2 btn-saffron text-sm flex items-center gap-1.5 py-2.5 px-5 rounded-lg"
              >
                Analyze Now <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Metrics */}
      <section className="container mx-auto px-4 -mt-16 relative z-20 pb-20">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {metrics.map((m, i) => (
            <motion.div
              key={m.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1, duration: 0.5 }}
              className="metric-card"
            >
              <div className="flex items-center gap-2 mb-3">
                <m.icon className={`h-4 w-4 ${m.color}`} />
                <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{m.label}</span>
              </div>
              <div className={`text-2xl ${m.color}`}>
                {m.text ? (
                  <span className="font-display font-bold text-lg">{m.text}</span>
                ) : (
                  <AnimatedCounter end={m.value} suffix={m.suffix} decimals={m.suffix === "/10" ? 1 : 1} />
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Quick Access */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { title: "AI Fake News Analyzer", desc: "Paste any claim or headline to get credibility scoring with AI-powered evidence analysis.", path: "/analyzer", icon: ShieldAlert },
            { title: "Public Pulse", desc: "Cast your civic vote on pressing issues and see age-wise opinion breakdowns.", path: "/public-pulse", icon: Users },
            { title: "Election Pulse", desc: "Participate in virtual elections and explore generational voting patterns.", path: "/election-pulse", icon: TrendingUp },
          ].map((card, i) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 + i * 0.15 }}
              onClick={() => navigate(card.path)}
              className="card-glass p-6 cursor-pointer group hover:border-primary/30 transition-all duration-300"
            >
              <card.icon className="h-8 w-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="font-display font-semibold text-lg mb-2">{card.title}</h3>
              <p className="text-sm text-muted-foreground">{card.desc}</p>
              <div className="mt-4 flex items-center gap-1 text-primary text-sm font-medium">
                Explore <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Index;
