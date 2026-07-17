import os
import re
import torch
import requests

from dotenv import load_dotenv
from app.services.llama_reasoner import llama_reason
from transformers import DistilBertTokenizerFast
from transformers import DistilBertForSequenceClassification
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load .env so TAVILY_API_KEY is available
load_dotenv()

# =========================================================
# MODEL LOADING
# =========================================================

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "models", "liar_model")

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH, local_files_only=True)
model     = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)
embedder  = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

labels = ["pants-fire", "false", "barely-true", "half-true", "mostly-true", "true"]

SOURCE_CREDIBILITY = {
    "wikipedia": 0.95,
    "bbc":       0.92,
    "reuters":   0.92,
    "nytimes":   0.88,
    "guardian":  0.88,
    "cnn":       0.82,
    "ndtv":      0.78,
    "espn":      0.75,
    "sky":       0.72,
}

REFUTE_WORDS = {
    "false", "debunked", "misleading", "incorrect", "not true",
    "hoax", "no evidence", "denied", "wrong", "misinformation",
    "fabricated", "inaccurate", "disputed", "refuted"
}
SUPPORT_WORDS = {
    "confirmed", "verified", "accurate", "official", "true",
    "correct", "established", "documented", "proven", "genuine"
}

# Wikipedia requires a proper User-Agent or returns 403
WIKI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FakeNewsDetector/1.0; research)"
}

# =========================================================
# HELPERS
# =========================================================

def get_source_credibility(url):
    url = url.lower()
    for source, score in SOURCE_CREDIBILITY.items():
        if source in url:
            return score
    return 0.5


def extract_entity(statement):
    """
    Extract the main named entity from a FEVER claim.

    FEVER claims always start with their subject:
      "Magic Johnson did not play..."  → "Magic Johnson"
      "Telemundo is a English..."      → "Telemundo"
      "Aristotle spent time..."        → "Aristotle"
      "Tim Roth is an English actor"   → "Tim Roth"

    Takes only leading capitalized words — stops at the
    first lowercase word which marks the verb/predicate.
    """
    cleaned = re.sub(
        r'^(the|a|an)\s+', '', statement.strip(),
        flags=re.IGNORECASE
    )
    words = cleaned.split()
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
    # Safety fallback
    if len(entity) < 3:
        entity = " ".join(words[:3])

    return entity


def predict_claim(statement):
    inputs = tokenizer(
        statement, return_tensors="pt",
        truncation=True, padding=True
    )
    with torch.no_grad():
        outputs = model(**inputs)

    probs    = torch.softmax(outputs.logits, dim=1)
    label_id = torch.argmax(probs).item()
    confidence = float(probs[0][label_id])
    label    = labels[label_id]

    # Get probability mass for each binary class
    # false_mass: pants-fire + false
    # true_mass: mostly-true + true
    # mixed_mass: barely-true + half-true
    false_mass = float(probs[0][0] + probs[0][1])
    mixed_mass = float(probs[0][2] + probs[0][3])
    true_mass  = float(probs[0][4] + probs[0][5])

    # Use probability mass instead of argmax
    # This prevents the model from defaulting to false
    # when true/false probabilities are close
    if false_mass > true_mass and false_mass > mixed_mass:
        return "false", false_mass
    elif true_mass > false_mass and true_mass > mixed_mass:
        return "true", true_mass
    else:
        return "mixed", mixed_mass

# =========================================================
# WIKIPEDIA RETRIEVAL
# =========================================================

def wikipedia_search(statement):
    """
    Entity-based Wikipedia lookup with User-Agent fix.

    Fix 1: Extract entity from statement (not full sentence)
    Fix 2: Send User-Agent header — Wikipedia returns 403
           for Python requests without it
    Fix 3: Two-stage fallback — direct lookup then search API
    """
    entity = extract_entity(statement)

    if not entity or len(entity) < 2:
        return []

    # ── Stage 1: Direct entity lookup ──────────────────────
    try:
        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + entity.replace(" ", "_")
        )
        r = requests.get(url, headers=WIKI_HEADERS, timeout=6)

        if r.status_code == 200:
            data    = r.json()
            extract = data.get("extract", "")
            title   = data.get("title", entity)

            if extract:
                return [{
                    "title":   title,
                    "url":     "https://en.wikipedia.org/wiki/"
                               + title.replace(" ", "_"),
                    "content": extract
                }]

    except Exception:
        pass

    # ── Stage 2: Search API fallback ───────────────────────
    try:
        sr = requests.get(
            "https://en.wikipedia.org/w/api.php",
            headers=WIKI_HEADERS,
            params={
                "action":   "query",
                "list":     "search",
                "srsearch": entity,
                "format":   "json",
                "srlimit":  1
            },
            timeout=6
        )
        results = sr.json().get("query", {}).get("search", [])

        if results:
            page_title = results[0]["title"]

            # Fetch full summary for the found page
            r2 = requests.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/"
                + page_title.replace(" ", "_"),
                headers=WIKI_HEADERS,
                timeout=6
            )
            if r2.status_code == 200:
                data2    = r2.json()
                extract2 = data2.get("extract", "")
                if extract2:
                    return [{
                        "title":   page_title,
                        "url":     "https://en.wikipedia.org/wiki/"
                                   + page_title.replace(" ", "_"),
                        "content": extract2
                    }]

            # Last resort — use search snippet
            snippet = re.sub(
                '<[^<]+?>', '',
                results[0].get("snippet", "")
            )
            if snippet:
                return [{
                    "title":   page_title,
                    "url":     "https://en.wikipedia.org/wiki/"
                               + page_title.replace(" ", "_"),
                    "content": snippet
                }]

    except Exception:
        pass

    return []

# =========================================================
# TAVILY RETRIEVAL
# =========================================================

def tavily_search(statement):
    """
    Tavily search for supplementary evidence.
    Uses "general" topic (not "news") — FEVER claims are
    factual encyclopedic statements, not news events.
    Requires TAVILY_API_KEY in .env file.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []

    evidence = []
    seen     = set()
    entity   = extract_entity(statement)

    queries = [
        statement,
        entity if len(entity) > 3 else statement,
    ]

    try:
        for q in queries:
            payload = {
                "api_key":     api_key,
                "query":       q,
                "topic":       "general",
                "max_results": 3
            }
            r = requests.post(
                "https://api.tavily.com/search",
                json=payload, timeout=7
            )
            for result in r.json().get("results", []):
                u = result.get("url", "")
                if u not in seen:
                    seen.add(u)
                    evidence.append({
                        "title":   result.get("title", ""),
                        "url":     u,
                        "content": result.get("content", "")
                    })

        return sorted(
            evidence,
            key=lambda x: get_source_credibility(x["url"]),
            reverse=True
        )[:6]

    except Exception:
        return []

# =========================================================
# EVIDENCE SIGNAL
# =========================================================

def get_evidence_signal(statement, evidence):
    """
    Directional signal with similarity fallback for neutral articles.

    For FEVER claims Wikipedia articles are encyclopedic —
    they rarely contain explicit support/refute keywords.
    So we use similarity as a weak positive signal for neutral
    articles, since high similarity = topically relevant evidence.
    """
    real_evidence = [
        e for e in evidence
        if e.get("url", "local") != "local"
    ]

    if not real_evidence:
        return 0.0, 0.0, False

    claim_vec = embedder.encode([statement])[0]
    texts     = [e["title"] + " " + e["content"] for e in real_evidence]
    vecs      = embedder.encode(texts)

    signals = []
    sims    = []

    for e, vec in zip(real_evidence, vecs):
        sim  = float(cosine_similarity([claim_vec], [vec])[0][0])
        cred = get_source_credibility(e["url"])
        text = (e["title"] + " " + e["content"]).lower()

        has_refute  = any(w in text for w in REFUTE_WORDS)
        has_support = any(w in text for w in SUPPORT_WORDS)

        if has_refute and not has_support:
            direction = -1.0
        elif has_support and not has_refute:
            direction = +1.0
        else:
            # Neutral article — use similarity as weak positive signal
            # High sim to Wikipedia = evidence exists and is relevant
            # This is the key fix for FEVER encyclopedic evidence
            direction = sim * 0.5

        if sim > 0.20:
            signals.append(sim * cred * direction)

        sims.append(sim)

    avg_signal = sum(signals) / len(signals) if signals else 0.0
    avg_sim    = sum(sims)    / len(sims)    if sims    else 0.0

    return avg_signal, avg_sim, True

# =========================================================
# FINAL HYBRID DECISION ENGINE
# =========================================================

def analyze_claim(statement):

    statement = statement.strip().lower()

    # ── Step 1: Baseline — always primary ──────────────────
    base_pred, confidence = predict_claim(statement)
    prediction = base_pred

    # ── Step 2: Retrieve evidence ───────────────────────────
    # Pass full statement — both functions extract entity internally
    wiki_evidence   = wikipedia_search(statement)
    tavily_evidence = tavily_search(statement)

    # Wikipedia first — highest credibility for FEVER claims
    evidence = wiki_evidence + tavily_evidence

    # ── Step 3: Directional evidence signal ─────────────────
    signal, avg_sim, has_real = get_evidence_signal(statement, evidence)

    # ── Step 4: Hybrid override ─────────────────────────────
    #
    # Override baseline ONLY when ALL three conditions met:
    #   (a) Real external evidence retrieved (not local fallback)
    #   (b) Model is uncertain — confidence < 0.60
    #   (c) Evidence signal is directionally strong |signal| > 0.15
    #
    # Baseline wins in all other cases.
    # Never force "mixed". Never flip without strong signal.

    # ── Step 4: Hybrid override ─────────────────────────────
    #
    # Key fixes from evaluation:
    # - Raised confidence threshold 0.60 → 0.80
    #   DistilBERT is overconfident on FEVER simple claims
    # - Lowered signal threshold 0.15 → 0.08
    #   Wikipedia articles are neutral/encyclopedic so signal
    #   is naturally lower than news articles
    # - Added similarity-only override for very high sim cases

    override_triggered = False

    if has_real and confidence < 0.80:

        if signal > 0.08:
            prediction         = "true"
            override_triggered = True

        elif signal < -0.08:
            prediction         = "false"
            override_triggered = True

    # Additional override — very high similarity to Wikipedia
    # with no strong model confidence means evidence is highly
    # relevant and should influence prediction
    elif has_real and avg_sim > 0.55 and confidence < 0.90:
        if signal >= 0:
            prediction         = "true"
            override_triggered = True
        else:
            prediction         = "false"
            override_triggered = True


    # ── Step 5: LLaMA for explanation ONLY ─────────────────
    # Never used to change prediction — LLaMA always mentions
    # "false"/"fake" in fact-checking context which caused
    # class collapse in all previous versions.

    try:
        top_ev       = evidence[:3] if evidence else []
        llama_output = llama_reason(statement, top_ev)
        reasoning    = llama_output.get("summary", "")
    except Exception:
        reasoning = ""

    if not reasoning:
        reasoning = (
            "Hybrid verification: DistilBERT classification "
            "combined with Wikipedia and web evidence retrieval."
        )

    # ── Step 6: Output ──────────────────────────────────────
    fake_probability = (
        confidence if prediction == "false" else 1 - confidence
    )

    return {
        "claim":              statement,
        "prediction":         prediction,
        "confidence":         round(float(confidence), 4),
        "fake_probability":   round(float(fake_probability), 4),
        "evidence_strength":  round(float(avg_sim), 4),
        "evidence_signal":    round(float(signal), 4),
        "has_real_evidence":  has_real,
        "override_triggered": override_triggered,
        "wiki_found":         len(wiki_evidence) > 0,
        "tavily_found":       len(tavily_evidence) > 0,
        "supporting_sources": len(evidence),
        "evidence":           evidence,
        "summary":            reasoning,
    }