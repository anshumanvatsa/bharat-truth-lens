import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis
} from "recharts";
import {
  Vote, MapPin, TrendingUp, Users, Lock,
  CheckCircle, AlertCircle, RefreshCw, LogIn
} from "lucide-react";
import {
  apiGetCandidates, apiGetResults, apiCastVote,
  apiGetMyVote, isLoggedIn, getProfile
} from "../lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────
interface Candidate {
  id: string;
  name: string;
  party: string;
  color: string;
}

interface Results {
  total_votes: number;
  candidates: Candidate[];
  overall: Record<string, { name: string; party: string; color: string; votes: number; percentage: number }>;
  by_age: Record<string, Record<string, { votes: number; percentage: number }>>;
  by_state: Record<string, { total: number; leading: string | null; leading_name: string | null }>;
}

// ── Party logos / icons mapping ───────────────────────────────────────────────
const PARTY_EMOJI: Record<string, string> = {
  BJP: "🪷", INC: "✋", AAP: "🧹", TMC: "🌺", JDU: "🔺", DMK: "🌊",
};

const AGE_GROUPS = ["18-25", "26-40", "41-60", "60+"];

const ElectionPulsePage = () => {
  const navigate = useNavigate();

  // Auth state
  const loggedIn = isLoggedIn();
  const profile  = getProfile() as Record<string, string> | null;

  // Data state
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [results, setResults]       = useState<Results | null>(null);
  const [myVote, setMyVote]         = useState<{ has_voted: boolean; candidate_id: string | null }>({
    has_voted: false, candidate_id: null,
  });

  // UI state
  const [selectedCandidate, setSelectedCandidate] = useState("");
  const [selectedAgeFilter, setSelectedAgeFilter] = useState("18-25");
  const [loading, setLoading]     = useState(true);
  const [voting, setVoting]       = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const [voted, setVoted]         = useState(false);

  // Load data on mount
  useEffect(() => {
    (async () => {
      try {
        const [cData, rData] = await Promise.all([
          apiGetCandidates(),
          apiGetResults(),
        ]);
        setCandidates(cData.candidates || []);
        setResults(rData);

        if (loggedIn) {
          const mv = await apiGetMyVote();
          setMyVote(mv);
          if (mv.has_voted) setVoted(true);
        }
      } catch {
        setError("Could not load election data. Is the backend running?");
      } finally {
        setLoading(false);
      }
    })();
  }, [loggedIn]);

  const handleVote = async () => {
    if (!selectedCandidate) return setError("Please select a candidate first.");
    setVoting(true);
    setError(null);
    try {
      await apiCastVote(selectedCandidate);
      setMyVote({ has_voted: true, candidate_id: selectedCandidate });
      setVoted(true);
      // Refresh results
      const rData = await apiGetResults();
      setResults(rData);
    } catch (err: any) {
      setError(err.message || "Vote failed. Please try again.");
    } finally {
      setVoting(false);
    }
  };

  const refreshResults = async () => {
    const rData = await apiGetResults();
    setResults(rData);
  };

  // ── Overall pie data ──────────────────────────────────────────────────────
  const pieData = results
    ? candidates.map((c) => ({
        name:       results.overall[c.id]?.name ?? c.name,
        value:      results.overall[c.id]?.votes ?? 0,
        percentage: results.overall[c.id]?.percentage ?? 0,
        fill:       c.color,
      }))
    : [];

  // ── Age-filtered bar data ─────────────────────────────────────────────────
  const ageBarData = results
    ? candidates.map((c) => ({
        name:  c.party,
        votes: results.by_age?.[selectedAgeFilter]?.[c.id]?.votes ?? 0,
        pct:   results.by_age?.[selectedAgeFilter]?.[c.id]?.percentage ?? 0,
        fill:  c.color,
      }))
    : [];

  // ── Top states for leading candidate ─────────────────────────────────────
  const topStates = results
    ? Object.entries(results.by_state)
        .filter(([, v]) => v.total > 0)
        .sort(([, a], [, b]) => b.total - a.total)
        .slice(0, 10)
    : [];

  // ── Loading ───────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent mx-auto" />
          <p className="text-muted-foreground text-sm">Loading election data…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <h1 className="font-display text-3xl md:text-4xl font-bold mb-2">
            Election <span className="text-gradient-saffron">Pulse</span>
          </h1>
          <p className="text-muted-foreground">
            Virtual PM opinion poll — one person, one vote. Real-time results by age group &amp; state.
          </p>
          {results && (
            <div className="flex items-center gap-2 mt-3">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-muted-foreground">
                {results.total_votes.toLocaleString()} votes cast so far
              </span>
              <button onClick={refreshResults} className="ml-2 text-primary hover:text-primary/80 transition-colors">
                <RefreshCw className="h-3.5 w-3.5" />
              </button>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 text-red-400 text-sm p-3 bg-red-500/10 rounded-lg border border-red-500/20 mb-6">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* ── LEFT: Voting Panel ──────────────────────────────────────── */}
          <div className="lg:col-span-1 space-y-4">

            {/* Auth gate */}
            {!loggedIn && (
              <motion.div
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                className="card-glass p-6 border border-primary/20 text-center"
              >
                <Lock className="h-8 w-8 text-primary mx-auto mb-3" />
                <h3 className="font-display font-semibold mb-2">Login to Vote</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  One person, one vote. Create a free account to cast your ballot and see your state's results.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => navigate("/signup")}
                    className="btn-saffron flex-1 py-2.5 text-sm"
                  >
                    Sign Up Free
                  </button>
                  <button
                    onClick={() => navigate("/login")}
                    className="flex-1 py-2.5 text-sm border border-border rounded-lg text-muted-foreground hover:border-muted-foreground/50 transition-all flex items-center justify-center gap-1.5"
                  >
                    <LogIn className="h-4 w-4" /> Login
                  </button>
                </div>
              </motion.div>
            )}

            {/* Profile badge */}
            {loggedIn && profile && (
              <div className="card-glass p-4 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm">
                  {(profile.full_name as string)?.[0]?.toUpperCase() ?? "U"}
                </div>
                <div>
                  <p className="font-medium text-sm">{profile.full_name as string}</p>
                  <p className="text-xs text-muted-foreground">
                    {profile.state as string} · Age {profile.age_group as string}
                  </p>
                </div>
                {voted && (
                  <div className="ml-auto">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                )}
              </div>
            )}

            {/* Already voted banner */}
            {voted && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="card-glass p-5 border border-green-500/30 bg-green-500/5"
              >
                <div className="flex items-center gap-2 text-green-400 mb-2">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-semibold text-sm">Vote Recorded!</span>
                </div>
                {myVote.candidate_id && (
                  <p className="text-sm text-muted-foreground">
                    You voted for{" "}
                    <span className="text-foreground font-medium">
                      {candidates.find((c) => c.id === myVote.candidate_id)?.name ?? "—"}
                    </span>
                  </p>
                )}
                <p className="text-xs text-muted-foreground mt-1">
                  One person, one vote — your ballot is final.
                </p>
              </motion.div>
            )}

            {/* Voting form — only if logged in and not yet voted */}
            {loggedIn && !voted && (
              <div className="card-glass p-6">
                <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                  <Vote className="h-5 w-5 text-primary" />
                  Cast Your Vote for PM
                </h3>
                <div className="space-y-3">
                  {candidates.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => setSelectedCandidate(c.id)}
                      className={`w-full p-4 rounded-xl border text-left transition-all ${
                        selectedCandidate === c.id
                          ? "border-primary bg-primary/5 ring-1 ring-primary/30"
                          : "border-border bg-muted/10 hover:border-muted-foreground/40"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{PARTY_EMOJI[c.party] ?? "🗳️"}</span>
                        <div className="flex-1">
                          <p className="font-semibold text-sm">{c.name}</p>
                          <p className="text-xs text-muted-foreground">{c.party}</p>
                        </div>
                        {selectedCandidate === c.id && (
                          <div className="w-4 h-4 rounded-full border-4 border-primary shrink-0" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
                <button
                  onClick={handleVote}
                  disabled={!selectedCandidate || voting}
                  className="btn-saffron w-full mt-5 py-3 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {voting ? (
                    <><div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" /> Casting vote…</>
                  ) : (
                    <><Vote className="h-4 w-4" /> Confirm Vote</>
                  )}
                </button>
                <p className="text-xs text-muted-foreground text-center mt-3">
                  🔒 Your vote is final. One person, one vote.
                </p>
              </div>
            )}
          </div>

          {/* ── RIGHT: Results Dashboard ────────────────────────────────── */}
          <div className="lg:col-span-2 space-y-6">

            {/* Overall Pie */}
            <div className="card-glass p-6">
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Overall Vote Share
                {results && <span className="ml-auto text-xs text-muted-foreground font-normal">{results.total_votes.toLocaleString()} total</span>}
              </h3>
              {results && results.total_votes > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        innerRadius={50}
                        strokeWidth={0}
                      >
                        {pieData.map((entry, i) => (
                          <Cell key={i} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(val: number, name: string) => [`${val} votes`, name]}
                        contentStyle={{ background: "hsl(216,48%,14%)", border: "1px solid hsl(216,30%,22%)", borderRadius: "8px", color: "hsl(210,40%,92%)" }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                    {candidates.map((c) => (
                      <div key={c.id} className="flex items-center gap-2 text-xs">
                        <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: c.color }} />
                        <span className="text-muted-foreground truncate">
                          {c.name} — <span className="text-foreground font-mono">{results.overall[c.id]?.percentage ?? 0}%</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="h-32 flex items-center justify-center text-muted-foreground text-sm">
                  No votes yet — be the first to vote!
                </div>
              )}
            </div>

            {/* Age-wise Bar */}
            <div className="card-glass p-6">
              <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                <h3 className="font-display font-semibold flex items-center gap-2">
                  <Users className="h-5 w-5 text-electric" />
                  Age-Wise Preference
                </h3>
                <div className="flex gap-1">
                  {AGE_GROUPS.map((ag) => (
                    <button
                      key={ag}
                      onClick={() => setSelectedAgeFilter(ag)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                        selectedAgeFilter === ag
                          ? "bg-primary text-white"
                          : "bg-muted/30 text-muted-foreground hover:bg-muted/50"
                      }`}
                    >
                      {ag}
                    </button>
                  ))}
                </div>
              </div>
              {results && results.total_votes > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={ageBarData} layout="horizontal">
                    <XAxis dataKey="name" stroke="hsl(215,20%,55%)" fontSize={11} />
                    <YAxis stroke="hsl(215,20%,55%)" fontSize={11} unit="%" />
                    <Tooltip
                      formatter={(val: number) => [`${val}%`, "Vote share"]}
                      contentStyle={{ background: "hsl(216,48%,14%)", border: "1px solid hsl(216,30%,22%)", borderRadius: "8px", color: "hsl(210,40%,92%)" }}
                    />
                    <Bar dataKey="pct" radius={[4, 4, 0, 0]}>
                      {ageBarData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-24 flex items-center justify-center text-muted-foreground text-sm">
                  Results will appear as votes come in.
                </div>
              )}
            </div>

            {/* State-wise Map Table */}
            <div className="card-glass p-6">
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <MapPin className="h-5 w-5 text-warning" />
                State-wise Lead
              </h3>
              {topStates.length > 0 ? (
                <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                  {topStates.map(([stateName, data]) => {
                    const cand = candidates.find((c) => c.id === data.leading);
                    return (
                      <div key={stateName} className="flex items-center gap-3 text-sm">
                        <span className="text-muted-foreground w-40 truncate shrink-0">{stateName}</span>
                        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${Math.min(100, (data.total / (topStates[0]?.[1]?.total || 1)) * 100)}%`,
                              background: cand?.color ?? "#888",
                            }}
                          />
                        </div>
                        <span className="text-xs font-mono w-16 text-right">{data.total} votes</span>
                        {cand && (
                          <span
                            className="text-xs font-medium w-24 truncate"
                            style={{ color: cand.color }}
                          >
                            {cand.name}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="h-20 flex items-center justify-center text-muted-foreground text-sm">
                  State results will appear once votes are cast.
                </div>
              )}
            </div>

          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ElectionPulsePage;
