import { motion } from "framer-motion";
import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { Vote, Users, TrendingUp, AlertTriangle } from "lucide-react";

const issues = [
  "Electoral Bond Transparency",
  "Education Policy Reform",
  "Farmer Protest Aftermath",
  "Digital Privacy Concerns",
  "Youth Unemployment Crisis",
];

const concernLevels = ["Low Concern", "Moderate Concern", "High Concern", "National Crisis"];
const concernColors = ["hsl(142, 76%, 46%)", "hsl(45, 93%, 47%)", "hsl(30, 100%, 60%)", "hsl(0, 72%, 51%)"];

const ageData = [
  { age: "18–25", concern: 78 },
  { age: "26–40", concern: 65 },
  { age: "41–60", concern: 52 },
  { age: "60+", concern: 41 },
];

const PublicPulsePage = () => {
  const [selectedIssue, setSelectedIssue] = useState("");
  const [voted, setVoted] = useState(false);
  const [selectedLevel, setSelectedLevel] = useState(-1);

  const handleVote = () => {
    if (selectedLevel >= 0 && selectedIssue) setVoted(true);
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto">
        <h1 className="font-display text-3xl md:text-4xl font-bold mb-2">
          Public <span className="text-gradient-electric">Pulse</span>
        </h1>
        <p className="text-muted-foreground mb-8">Voice your opinion on critical issues and see how your generation compares.</p>

        {!voted ? (
          <div className="space-y-6">
            <div className="card-glass p-6">
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <Vote className="h-5 w-5 text-primary" /> Select an Issue
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {issues.map((issue) => (
                  <button
                    key={issue}
                    onClick={() => setSelectedIssue(issue)}
                    className={`p-4 rounded-lg border text-left text-sm font-medium transition-all ${
                      selectedIssue === issue
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border bg-muted/20 text-muted-foreground hover:border-muted-foreground/40"
                    }`}
                  >
                    {issue}
                  </button>
                ))}
              </div>
            </div>

            {selectedIssue && (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="card-glass p-6">
                <h3 className="font-display font-semibold mb-4">How serious is "{selectedIssue}"?</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {concernLevels.map((level, i) => (
                    <button
                      key={level}
                      onClick={() => setSelectedLevel(i)}
                      className={`p-4 rounded-lg border text-center text-sm font-medium transition-all ${
                        selectedLevel === i
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border bg-muted/20 text-muted-foreground hover:border-muted-foreground/40"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
                <button onClick={handleVote} disabled={selectedLevel < 0} className="btn-saffron mt-6 disabled:opacity-50">
                  Submit Vote
                </button>
              </motion.div>
            )}
          </div>
        ) : (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <div className="card-glass p-6 text-center">
              <div className="text-4xl mb-2">🗳</div>
              <h3 className="font-display font-semibold text-lg mb-1">Vote Recorded!</h3>
              <p className="text-sm text-muted-foreground">Your voice matters. Here's how the nation thinks about "{selectedIssue}".</p>
            </div>

            <div className="card-glass p-6">
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <Users className="h-5 w-5 text-electric" /> Age-Wise Concern Breakdown
              </h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={ageData}>
                  <XAxis dataKey="age" stroke="hsl(215, 20%, 55%)" fontSize={12} />
                  <YAxis stroke="hsl(215, 20%, 55%)" fontSize={12} />
                  <Tooltip contentStyle={{ background: "hsl(216, 48%, 14%)", border: "1px solid hsl(216, 30%, 22%)", borderRadius: "8px", color: "hsl(210, 40%, 92%)" }} />
                  <Bar dataKey="concern" radius={[6, 6, 0, 0]}>
                    {ageData.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? "hsl(30, 100%, 60%)" : "hsl(199, 92%, 64%)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="metric-card text-center">
                <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Youth Concern Index</p>
                <p className="text-3xl font-mono font-bold text-primary">78%</p>
              </div>
              <div className="metric-card text-center">
                <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Senior Concern Index</p>
                <p className="text-3xl font-mono font-bold text-electric">41%</p>
              </div>
              <div className="metric-card text-center">
                <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Civic Priority Score</p>
                <p className="text-3xl font-mono font-bold text-warning">6.8/10</p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default PublicPulsePage;
