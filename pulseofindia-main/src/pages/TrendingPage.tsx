import { motion } from "framer-motion";
import { useState } from "react";
import { Search, TrendingDown, AlertTriangle, Calendar, BarChart3, Clock } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

const trendingCases = [
  {
    title: "Electoral Bond Case",
    peakMonth: "Feb 2024",
    currentCoverage: 12,
    attentionDrop: 87,
    severity: 8.4,
    youthConcern: 72,
    timeline: [
      { month: "Jan", articles: 45 }, { month: "Feb", articles: 320 }, { month: "Mar", articles: 280 },
      { month: "Apr", articles: 150 }, { month: "May", articles: 80 }, { month: "Jun", articles: 42 },
      { month: "Jul", articles: 28 }, { month: "Aug", articles: 15 }, { month: "Sep", articles: 12 },
    ],
    events: [
      { month: "Feb 2024", event: "SC strikes down Electoral Bond Scheme", type: "spike" },
      { month: "Apr 2024", event: "SBI releases bond data", type: "update" },
      { month: "Jul 2024", event: "Investigation slows", type: "silence" },
    ],
    summary: "Supreme Court struck down the Electoral Bond scheme as unconstitutional. Despite massive initial coverage, media attention has dropped significantly.",
    legalStatus: "Under investigation — multiple PILs pending in various High Courts.",
  },
  {
    title: "Porsche Accident Case",
    peakMonth: "May 2024",
    currentCoverage: 8,
    attentionDrop: 91,
    severity: 7.2,
    youthConcern: 68,
    timeline: [
      { month: "Apr", articles: 10 }, { month: "May", articles: 290 }, { month: "Jun", articles: 180 },
      { month: "Jul", articles: 75 }, { month: "Aug", articles: 30 }, { month: "Sep", articles: 12 },
    ],
    events: [
      { month: "May 2024", event: "Juvenile kills two in Porsche hit-and-run", type: "spike" },
      { month: "Jun 2024", event: "Juvenile Board grants bail", type: "update" },
      { month: "Aug 2024", event: "Media coverage fades", type: "silence" },
    ],
    summary: "A minor from an affluent family killed two people in a hit-and-run. Questions about juvenile justice and privilege dominated headlines.",
    legalStatus: "Case transferred to Juvenile Justice Board — trial ongoing.",
  },
  {
    title: "Farmer Protest 2.0",
    peakMonth: "Feb 2024",
    currentCoverage: 5,
    attentionDrop: 94,
    severity: 7.8,
    youthConcern: 58,
    timeline: [
      { month: "Jan", articles: 30 }, { month: "Feb", articles: 350 }, { month: "Mar", articles: 200 },
      { month: "Apr", articles: 90 }, { month: "May", articles: 40 }, { month: "Jun", articles: 18 },
    ],
    events: [
      { month: "Feb 2024", event: "Farmers march to Delhi", type: "spike" },
      { month: "Mar 2024", event: "Government talks begin", type: "update" },
      { month: "May 2024", event: "Protest called off temporarily", type: "silence" },
    ],
    summary: "Farmers renewed protests demanding legal MSP guarantee. After initial coverage surge, media attention dropped sharply.",
    legalStatus: "Negotiations ongoing — committee formed by central government.",
  },
];

const TrendingPage = () => {
  const [selectedCase, setSelectedCase] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCases = trendingCases.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="container mx-auto px-4 py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="max-w-5xl mx-auto">
        <h1 className="font-display text-3xl md:text-4xl font-bold mb-2">
          Trending <span className="text-gradient-saffron">Case Tracker</span>
        </h1>
        <p className="text-muted-foreground mb-8">Track cases that dominated headlines — and discover what happened next.</p>

        {/* What Happened Next Search */}
        <div className="card-glass p-6 mb-8">
          <h3 className="font-display font-semibold mb-3 flex items-center gap-2">
            <Search className="h-5 w-5 text-electric" /> "What Happened Next?" Search
          </h3>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search past headline (e.g., Porsche Case 2024, Farmer Protest 2023)"
              className="w-full pl-11 pr-4 py-3 bg-muted/30 border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
            />
          </div>
        </div>

        {/* Case Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {filteredCases.map((c, i) => (
            <motion.div
              key={c.title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              onClick={() => setSelectedCase(selectedCase === i ? null : i)}
              className={`metric-card cursor-pointer ${selectedCase === i ? "border-primary/50 glow-saffron" : ""}`}
            >
              <h4 className="font-display font-semibold mb-3">{c.title}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Peak Month</span>
                  <span className="font-mono">{c.peakMonth}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Coverage</span>
                  <span className="font-mono">{c.currentCoverage}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Attention Drop</span>
                  <span className="font-mono text-destructive flex items-center gap-1">
                    {c.attentionDrop > 80 && <AlertTriangle className="h-3 w-3" />}
                    {c.attentionDrop}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Severity</span>
                  <span className="font-mono text-primary">{c.severity}/10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Youth Concern</span>
                  <span className="font-mono text-electric">{c.youthConcern}%</span>
                </div>
              </div>
              {c.attentionDrop > 80 && (
                <div className="mt-3 px-2 py-1 bg-destructive/10 border border-destructive/20 rounded text-xs text-destructive text-center">
                  ⚠ Media Attention Dropped by {c.attentionDrop}%
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Expanded Case Detail */}
        {selectedCase !== null && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <div className="card-glass p-6">
              <h3 className="font-display font-semibold text-xl mb-2">{trendingCases[selectedCase].title}</h3>
              <p className="text-muted-foreground text-sm mb-4">{trendingCases[selectedCase].summary}</p>

              <div className="p-3 bg-muted/30 rounded-lg mb-4">
                <p className="text-sm"><span className="text-electric font-medium">Legal Status:</span> {trendingCases[selectedCase].legalStatus}</p>
              </div>
            </div>

            {/* Media Attention Decay */}
            <div className="card-glass p-6">
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-destructive" /> Media Attention Decay
              </h3>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={trendingCases[selectedCase].timeline}>
                  <defs>
                    <linearGradient id="decayGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(30, 100%, 60%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(30, 100%, 60%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="month" stroke="hsl(215, 20%, 55%)" fontSize={12} />
                  <YAxis stroke="hsl(215, 20%, 55%)" fontSize={12} />
                  <Tooltip contentStyle={{ background: "hsl(216, 48%, 14%)", border: "1px solid hsl(216, 30%, 22%)", borderRadius: "8px", color: "hsl(210, 40%, 92%)" }} />
                  <Area type="monotone" dataKey="articles" stroke="hsl(30, 100%, 60%)" fill="url(#decayGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Timeline */}
            <div className="card-glass p-6">
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-electric" /> Event Timeline
              </h3>
              <div className="space-y-4">
                {trendingCases[selectedCase].events.map((e, i) => (
                  <div key={i} className="flex gap-4 items-start">
                    <div className={`w-3 h-3 rounded-full mt-1.5 shrink-0 ${
                      e.type === "spike" ? "bg-primary" : e.type === "update" ? "bg-electric" : "bg-muted-foreground"
                    }`} />
                    <div>
                      <p className="text-xs text-muted-foreground font-mono">{e.month}</p>
                      <p className="text-sm">{e.event}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default TrendingPage;
