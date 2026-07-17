import { motion } from "framer-motion";
import { useState } from "react";
import { Search, User, Scale, IndianRupee, GraduationCap, TrendingUp, ThumbsUp, AlertTriangle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const leaders = [
  {
    name: "Rajesh Kumar",
    party: "National Progress Party",
    education: "MBA — IIM Ahmedabad",
    assets: "₹12.4 Crore",
    criminalCases: 0,
    promises: { total: 24, completed: 14, inProgress: 6, unfulfilled: 4 },
    youthApproval: 68,
    civicRating: 7.2,
    sentiment: [
      { month: "Jan", rating: 65 }, { month: "Feb", rating: 68 }, { month: "Mar", rating: 72 },
      { month: "Apr", rating: 70 }, { month: "May", rating: 74 }, { month: "Jun", rating: 68 },
    ],
  },
  {
    name: "Sunita Devi",
    party: "People's Alliance",
    education: "LLB — Delhi University",
    assets: "₹8.7 Crore",
    criminalCases: 2,
    promises: { total: 18, completed: 5, inProgress: 8, unfulfilled: 5 },
    youthApproval: 54,
    civicRating: 5.8,
    sentiment: [
      { month: "Jan", rating: 52 }, { month: "Feb", rating: 55 }, { month: "Mar", rating: 54 },
      { month: "Apr", rating: 58 }, { month: "May", rating: 56 }, { month: "Jun", rating: 54 },
    ],
  },
  {
    name: "Amit Verma",
    party: "Democratic Front",
    education: "B.Tech — IIT Delhi",
    assets: "₹22.1 Crore",
    criminalCases: 1,
    promises: { total: 30, completed: 8, inProgress: 12, unfulfilled: 10 },
    youthApproval: 45,
    civicRating: 4.9,
    sentiment: [
      { month: "Jan", rating: 48 }, { month: "Feb", rating: 46 }, { month: "Mar", rating: 45 },
      { month: "Apr", rating: 44 }, { month: "May", rating: 46 }, { month: "Jun", rating: 45 },
    ],
  },
];

const LeadersPage = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLeader, setSelectedLeader] = useState<number | null>(null);

  const filtered = leaders.filter((l) => l.name.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="container mx-auto px-4 py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="max-w-5xl mx-auto">
        <h1 className="font-display text-3xl md:text-4xl font-bold mb-2">
          Politician <span className="text-gradient-electric">Profile Tracker</span>
        </h1>
        <p className="text-muted-foreground mb-8">Transparency dashboard for elected leaders — promises, assets, and public sentiment.</p>

        <div className="relative mb-8">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search politician…"
            className="w-full pl-11 pr-4 py-3 bg-card/80 border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {filtered.map((l, i) => (
            <motion.div
              key={l.name}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              onClick={() => setSelectedLeader(selectedLeader === i ? null : i)}
              className={`metric-card cursor-pointer ${selectedLeader === i ? "border-primary/50 glow-saffron" : ""}`}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                  <User className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h4 className="font-display font-semibold">{l.name}</h4>
                  <p className="text-xs text-muted-foreground">{l.party}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Youth Approval</span>
                  <span className="font-mono text-electric">{l.youthApproval}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Civic Rating</span>
                  <span className="font-mono text-primary">{l.civicRating}/10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Criminal Cases</span>
                  <span className={`font-mono ${l.criminalCases > 0 ? "text-destructive" : "text-success"}`}>{l.criminalCases}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {selectedLeader !== null && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            {(() => {
              const l = leaders[selectedLeader];
              const pct = (v: number) => ((v / l.promises.total) * 100).toFixed(0);
              return (
                <>
                  <div className="card-glass p-6">
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                        <User className="h-8 w-8 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-display text-xl font-bold">{l.name}</h3>
                        <p className="text-muted-foreground text-sm">{l.party}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="flex items-center gap-2 text-sm">
                        <GraduationCap className="h-4 w-4 text-electric" />
                        <span className="text-muted-foreground">{l.education}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <IndianRupee className="h-4 w-4 text-primary" />
                        <span className="text-muted-foreground">Assets: {l.assets}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Scale className="h-4 w-4 text-warning" />
                        <span className="text-muted-foreground">Cases: {l.criminalCases}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <ThumbsUp className="h-4 w-4 text-success" />
                        <span className="text-muted-foreground">Youth: {l.youthApproval}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Promise Tracker */}
                  <div className="card-glass p-6">
                    <h3 className="font-display font-semibold mb-4">Promise Tracker ({l.promises.total} total)</h3>
                    <div className="space-y-3">
                      {[
                        { label: "Completed", value: l.promises.completed, color: "bg-success" },
                        { label: "In Progress", value: l.promises.inProgress, color: "bg-electric" },
                        { label: "Unfulfilled", value: l.promises.unfulfilled, color: "bg-destructive" },
                      ].map((p) => (
                        <div key={p.label}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-muted-foreground">{p.label}</span>
                            <span className="font-mono">{pct(p.value)}% ({p.value})</span>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${pct(p.value)}%` }}
                              transition={{ duration: 1 }}
                              className={`h-full rounded-full ${p.color}`}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Sentiment Trend */}
                  <div className="card-glass p-6">
                    <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-primary" /> Public Sentiment Trend
                    </h3>
                    <ResponsiveContainer width="100%" height={220}>
                      <LineChart data={l.sentiment}>
                        <XAxis dataKey="month" stroke="hsl(215, 20%, 55%)" fontSize={12} />
                        <YAxis stroke="hsl(215, 20%, 55%)" fontSize={12} domain={[30, 100]} />
                        <Tooltip contentStyle={{ background: "hsl(216, 48%, 14%)", border: "1px solid hsl(216, 30%, 22%)", borderRadius: "8px", color: "hsl(210, 40%, 92%)" }} />
                        <Line type="monotone" dataKey="rating" stroke="hsl(30, 100%, 60%)" strokeWidth={2} dot={{ fill: "hsl(30, 100%, 60%)", r: 4 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </>
              );
            })()}
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default LeadersPage;
