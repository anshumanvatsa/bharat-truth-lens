"""
analyzer_cloud.py — Lightweight production analyzer (no PyTorch/transformers)

Uses:
  - Groq API (LLaMA-3.1-8B) for claim classification + explanation
  - Wikipedia REST API for evidence retrieval
  - Tavily API for web evidence

Memory footprint: ~80MB (vs ~650MB with PyTorch + DistilBERT)
Suitable for: Render free tier (512MB limit)
"""

import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

WIKI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BharatTruthLens/1.0; research)"
}

SOURCE_CREDIBILITY = {
    "wikipedia": 0.95, "bbc": 0.92, "reuters": 0.92,
    "nytimes": 0.88,   "guardian": 0.88, "cnn": 0.82,
    "ndtv": 0.78,      "thehindu": 0.78, "timesofindia": 0.72,
}

SEVERITY_KEYWORDS = {
    "economic":  ["economy","gdp","inflation","tax","budget","rupee","market",
                  "price","trade","employment","jobs","income","poverty",
                  "financial","bank","investment","subsidy","currency"],
    "social":    ["caste","religion","minority","community","protest","riot",
                  "gender","education","health","discrimination","rights",
                  "farmer","student","women","youth","violence","mob"],
    "political": ["election","vote","party","government","minister","parliament",
                  "bjp","congress","opposition","policy","law","bill","court",
                  "constitution","modi","rahul","chief minister","lok sabha"],
    "national":  ["india","pakistan","china","border","army","military",
                  "national","security","terrorism","kashmir","defence",
                  "sovereignty","nuclear","diplomatic","foreign"],
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_source_credibility(url: str) -> float:
    url = url.lower()
    for src, score in SOURCE_CREDIBILITY.items():
        if src in url:
            return score
    return 0.5


def extract_entity(statement: str) -> str:
    cleaned = re.sub(r'^(the|a|an)\s+', '', statement.strip(), flags=re.IGNORECASE)
    words   = cleaned.split()
    if not words:
        return statement
    entity_words = [words[0]]
    for w in words[1:]:
        alpha = re.sub(r'[^a-zA-Z]', '', w)
        if alpha and alpha[0].isupper() and len(alpha) > 1:
            entity_words.append(w)
        else:
            break
    entity = " ".join(entity_words)
    return entity if len(entity) >= 3 else " ".join(words[:3])


def compute_severity(claim: str, evidence_texts: list) -> dict:
    combined = (claim + " " + " ".join(evidence_texts)).lower()
    scores   = {}
    for dim, keywords in SEVERITY_KEYWORDS.items():
        hits        = sum(1 for kw in keywords if kw in combined)
        scores[dim] = min(100, int(10 + (hits / len(keywords)) * 90))
    return scores


# ── Wikipedia retrieval ───────────────────────────────────────────────────────

def wikipedia_search(statement: str) -> list:
    entity = extract_entity(statement)
    if not entity or len(entity) < 2:
        return []

    # Stage 1: direct lookup
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{entity.replace(' ', '_')}",
            headers=WIKI_HEADERS, timeout=6
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("extract"):
                return [{
                    "title":   data.get("title", entity),
                    "url":     f"https://en.wikipedia.org/wiki/{data.get('title','').replace(' ','_')}",
                    "content": data["extract"],
                }]
    except Exception:
        pass

    # Stage 2: search API fallback
    try:
        sr = requests.get(
            "https://en.wikipedia.org/w/api.php",
            headers=WIKI_HEADERS,
            params={"action":"query","list":"search","srsearch":entity,
                    "format":"json","srlimit":1},
            timeout=6
        )
        results = sr.json().get("query", {}).get("search", [])
        if results:
            title = results[0]["title"]
            r2    = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ','_')}",
                headers=WIKI_HEADERS, timeout=6
            )
            if r2.status_code == 200 and r2.json().get("extract"):
                return [{
                    "title":   title,
                    "url":     f"https://en.wikipedia.org/wiki/{title.replace(' ','_')}",
                    "content": r2.json()["extract"],
                }]
    except Exception:
        pass

    return []


def tavily_search(statement: str) -> list:
    if not TAVILY_API_KEY:
        return []
    entity   = extract_entity(statement)
    evidence = []
    seen     = set()
    try:
        for q in [statement, entity]:
            r = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": TAVILY_API_KEY, "query": q,
                      "topic": "general", "max_results": 3},
                timeout=7
            )
            for result in r.json().get("results", []):
                u = result.get("url", "")
                if u not in seen:
                    seen.add(u)
                    evidence.append({
                        "title":   result.get("title", ""),
                        "url":     u,
                        "content": result.get("content", ""),
                    })
        return sorted(evidence, key=lambda x: get_source_credibility(x["url"]),
                      reverse=True)[:6]
    except Exception:
        return []


# ── Groq classification + explanation ────────────────────────────────────────

def groq_analyze(claim: str, evidence: list) -> dict:
    """
    Use Groq LLaMA-3 to:
    1. Classify the claim (TRUE / FALSE / MISLEADING)
    2. Explain the verdict using the evidence
    Returns parsed result dict.
    """
    if not GROQ_API_KEY:
        return _fallback_result(claim, evidence)

    evidence_block = ""
    for i, e in enumerate(evidence[:4]):
        evidence_block += f"{i+1}. {e.get('title','')} — {e.get('content','')[:250]}\n"

    prompt = f"""You are an AI fact-checking assistant specialising in Indian news and politics.

Claim to verify:
"{claim}"

Evidence from trusted sources:
{evidence_block if evidence_block else "No external evidence retrieved."}

Instructions:
1. Compare the claim against the evidence carefully.
2. Return EXACTLY this format (no extra text):

VERDICT: TRUE | FALSE | MISLEADING
CONFIDENCE: HIGH | MEDIUM | LOW
PREDICTION: true | false | mixed
REASON: 2-3 sentences explaining your verdict, citing the evidence.
"""

    try:
        from groq import Groq
        client   = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=220,
            temperature=0.1,
        )
        text = response.choices[0].message.content.strip()
        return _parse_groq_response(text, claim, evidence)
    except Exception as e:
        print(f"[GroqAnalyzer] Error: {e}")
        return _fallback_result(claim, evidence)


def _parse_groq_response(text: str, claim: str, evidence: list) -> dict:
    lines = text.upper()

    # Extract prediction
    prediction = "mixed"
    if "PREDICTION: TRUE" in lines or "VERDICT: TRUE" in lines:
        prediction = "true"
    elif "PREDICTION: FALSE" in lines or "VERDICT: FALSE" in lines:
        prediction = "false"

    # Extract confidence
    confidence_label = "MEDIUM"
    if "CONFIDENCE: HIGH" in lines:
        confidence_label = "HIGH"
    elif "CONFIDENCE: LOW" in lines:
        confidence_label = "LOW"

    confidence_score = {"HIGH": 0.85, "MEDIUM": 0.65, "LOW": 0.45}[confidence_label]

    # Source counts
    supporting = sum(1 for e in evidence if prediction == "true")
    refuting   = sum(1 for e in evidence if prediction == "false")
    if prediction == "true":
        supporting = min(len(evidence), 3)
        refuting   = 0
    elif prediction == "false":
        refuting   = min(len(evidence), 3)
        supporting = 0
    else:
        supporting = len(evidence) // 2
        refuting   = len(evidence) - supporting

    evidence_texts = [e.get("title","") + " " + e.get("content","") for e in evidence]
    severity       = compute_severity(claim, evidence_texts)

    indian_sources = sum(
        1 for e in evidence
        if any(s in e.get("url","").lower()
               for s in ["ndtv","thehindu","timesofindia","hindustantimes","india"])
    )

    return {
        "summary":            text,
        "prediction":         prediction,
        "confidence":         round(confidence_score, 4),
        "fake_probability":   round(1 - confidence_score if prediction == "true" else confidence_score, 4),
        "evidence_strength":  0.6 if evidence else 0.3,
        "evidence_signal":    0.1 if prediction == "true" else -0.1 if prediction == "false" else 0.0,
        "has_real_evidence":  len(evidence) > 0,
        "override_triggered": False,
        "wiki_found":         any("wikipedia" in e.get("url","") for e in evidence),
        "tavily_found":       any("wikipedia" not in e.get("url","") for e in evidence),
        "supporting_sources": supporting,
        "refuting_sources":   refuting,
        "evidence":           evidence,
        "indian_sources":     indian_sources,
        "global_sources":     len(evidence),
        "severity":           severity,
    }


def _fallback_result(claim: str, evidence: list) -> dict:
    evidence_texts = [e.get("title","") + " " + e.get("content","") for e in evidence]
    severity = compute_severity(claim, evidence_texts)
    return {
        "summary": (
            "Verdict: MISLEADING\n"
            "Confidence: LOW\n"
            "Reason: Analysis service temporarily unavailable. "
            "Please review the evidence sources manually."
        ),
        "prediction":         "mixed",
        "confidence":         0.4,
        "fake_probability":   0.5,
        "evidence_strength":  0.3,
        "evidence_signal":    0.0,
        "has_real_evidence":  len(evidence) > 0,
        "override_triggered": False,
        "wiki_found":         any("wikipedia" in e.get("url","") for e in evidence),
        "tavily_found":       False,
        "supporting_sources": 0,
        "refuting_sources":   0,
        "evidence":           evidence,
        "indian_sources":     0,
        "global_sources":     len(evidence),
        "severity":           severity,
    }


# ── Main public function ──────────────────────────────────────────────────────

def analyze_claim_cloud(statement: str) -> dict:
    """
    Cloud-lightweight claim analysis.
    No PyTorch, no transformers, no local models.
    Uses Groq (LLaMA-3) + Wikipedia + Tavily.
    """
    statement = statement.strip()

    # 1. Retrieve evidence
    wiki    = wikipedia_search(statement)
    tavily  = tavily_search(statement)
    evidence = wiki + tavily

    # 2. Classify + explain with Groq
    result = groq_analyze(statement, evidence)
    result["claim"] = statement
    return result
