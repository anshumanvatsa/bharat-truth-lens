import { motion } from "framer-motion";
import { useState } from "react";
import {
  Search,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Globe,
  FileText
} from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";

import AnimatedCounter from "../components/AnimatedCounter";

const AnalyzerPage = () => {

  const [text, setText] = useState("");
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {

    if (!text.trim()) return;

    setLoading(true);
    setAnalyzed(false);
    setError(null);

    try {

      const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${API_URL}/analyze/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ claim: text })
      });

      if (!res.ok) {
        throw new Error("Backend request failed");
      }

      const data = await res.json();
      console.log("API response:", data);

      const credibility = (data.confidence ?? 0) * 10;

      /* FIX 1: Use backend fake_probability instead of recalculating */
      const fakeProbability = (data.fake_probability ?? 0) * 100;

      const evidenceScore = Math.round((data.evidence_strength ?? 0.3) * 100);

      setResults({

        credibility,
        fakeProbability,
        evidenceScore,

        evidence: data.evidence ?? [],

        sources: [
          {
            name: "Supporting",
            value: data.supporting_sources ?? 0,
            color: "#22c55e"
          },
          {
            name: "Refuting",
            value: data.refuting_sources ?? 0,
            color: "#ef4444"
          }
        ],

        indianSources: data.indian_sources ?? 0,
        globalSources: data.global_sources ?? 0,

        severity: data.severity ?? {
          economic: 40,
          social: 60,
          political: 70,
          national: 30
        },

        summary: data.summary ?? "No AI reasoning available.",

        /* FIX 2: normalize prediction string */
        prediction: data.prediction?.toLowerCase().trim()

      });

      setAnalyzed(true);

    } catch (err) {

      console.error("Analyzer error:", err);
      setError("Could not connect to the analysis server. Please try again or check that the backend is running.");

    } finally {

      setLoading(false);

    }

  };

  const credibilityValue = results?.credibility ?? 0;

  const credibilityColor =
    credibilityValue > 7
      ? "text-green-500"
      : credibilityValue > 4
      ? "text-yellow-500"
      : "text-red-500";

  const credibilityLabel =
    credibilityValue > 7
      ? "High Credibility"
      : credibilityValue > 4
      ? "Moderate Credibility"
      : "Low Credibility";

  const fakeColor =
    results?.prediction === "true"
      ? "text-green-500"
      : results?.prediction === "mixed"
      ? "text-yellow-500"
      : "text-red-500";

  return (

    <div className="container mx-auto px-4 py-12">

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-5xl mx-auto"
      >

        <h1 className="text-3xl md:text-4xl font-bold mb-2">
          AI Fake News & <span className="text-orange-500">Severity Analyzer</span>
        </h1>

        <p className="text-muted-foreground mb-8">
          Paste any claim or headline for AI-powered credibility analysis.
        </p>

        {/* INPUT */}

        <div className="card-glass p-6 mb-8">

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            placeholder="Paste the claim here..."
            className="w-full bg-muted/30 border rounded-lg p-4"
          />

          <button
            onClick={handleAnalyze}
            className="btn-saffron mt-4 flex items-center gap-2"
          >
            <Search className="h-4 w-4" />
            Analyze Claim
          </button>

          {loading && (
            <div className="mt-4 flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-orange-500 border-t-transparent" />
              <p className="text-sm text-muted-foreground">
                Analyzing claim — fetching Wikipedia &amp; web evidence...
              </p>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 text-red-400 text-sm mt-3 p-3 bg-red-500/10 rounded-lg border border-red-500/20">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

        </div>

        {analyzed && results && (

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >

            {/* SCORE ROW */}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

              <div className="metric-card text-center">

                <p className="text-xs uppercase mb-2">Credibility Score</p>

                <div className="text-4xl font-bold">
                  {credibilityValue.toFixed(1)}
                </div>

                <p className={`text-sm ${credibilityColor}`}>
                  {credibilityLabel}
                </p>

              </div>

              <div className="metric-card text-center">

                <p className="text-xs uppercase mb-2">Fake Probability</p>

                <div className={`text-4xl ${fakeColor}`}>
                  <AnimatedCounter end={results.fakeProbability} suffix="%" />
                </div>

              </div>

              <div className="metric-card text-center">

                <p className="text-xs uppercase mb-2">Evidence Score</p>

                <div className="text-4xl text-yellow-400">
                  <AnimatedCounter end={results.evidenceScore} suffix="%" />
                </div>

              </div>

            </div>

            {/* SOURCE CHART */}

            <div className="card-glass p-6">

              <h3 className="font-semibold mb-4 flex gap-2 items-center">
                <BarChart3 className="h-5 w-5" />
                Supporting vs Refuting Sources
              </h3>

              <ResponsiveContainer width="100%" height={200}>

                <BarChart data={results.sources}>

                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />

                  <Bar dataKey="value">

                    {results.sources.map((s: any, i: number) => (
                      <Cell key={i} fill={s.color} />
                    ))}

                  </Bar>

                </BarChart>

              </ResponsiveContainer>

              <div className="flex gap-6 mt-4 text-sm">

                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  Indian Sources: {results.indianSources}
                </div>

                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  Global Sources: {results.globalSources}
                </div>

              </div>

            </div>

            {/* AI SUMMARY */}

            <div className="card-glass p-6">

              <h3 className="font-semibold mb-3 flex gap-2 items-center">
                <FileText className="h-5 w-5" />
                AI Evidence Summary
              </h3>

              <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
                {results.summary}
              </p>

            </div>

            {/* EVIDENCE SOURCES */}

            {results.evidence?.length > 0 && (

              <div className="card-glass p-6">

                <h3 className="font-semibold mb-4 flex gap-2 items-center">
                  <Globe className="h-5 w-5" />
                  Evidence Sources
                </h3>

                <div className="space-y-4">

                  {results.evidence.map((item: any, i: number) => (

                    <a
                      key={i}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-4 border rounded-lg hover:bg-muted/20 transition"
                    >

                      <h4 className="font-semibold text-blue-400 text-sm">
                        {item.title}
                      </h4>

                      <p className="text-xs text-muted-foreground mt-1">
                        {item.content?.slice(0, 150)}...
                      </p>

                    </a>

                  ))}

                </div>

              </div>

            )}

            {/* SEVERITY BREAKDOWN */}

            <div className="card-glass p-6">

              <h3 className="font-semibold mb-4">
                Severity Breakdown
              </h3>

              <div className="space-y-4">

                {Object.entries(results.severity).map(([key, val]: any) => (

                  <div key={key}>

                    <div className="flex justify-between text-sm mb-1">
                      <span className="capitalize">{key}</span>
                      <span>{val}%</span>
                    </div>

                    <div className="h-2 bg-gray-700 rounded-full">

                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${val}%` }}
                        transition={{ duration: 1 }}
                        className={`h-2 rounded-full ${
                          val > 70
                            ? "bg-red-500"
                            : val > 40
                            ? "bg-yellow-400"
                            : "bg-green-500"
                        }`}
                      />

                    </div>

                  </div>

                ))}

              </div>

            </div>

            {/* CIVIC VOTE BUTTON */}

            <div className="text-center pt-6">

              <button
                onClick={() => window.location.href = "/public-pulse"}
                className="btn-saffron text-lg px-8 py-4 rounded-xl"
              >
                🗳 Cast Your Civic Vote
              </button>

            </div>

          </motion.div>

        )}

      </motion.div>

    </div>

  );

};

export default AnalyzerPage;