import os
import re

from dotenv import load_dotenv
load_dotenv()

# =========================================================
# GROQ API (primary for production — free, fast LLaMA-3)
# LOCAL LLAMA (fallback for offline/local use)
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Use Groq if API key is configured
USE_GROQ = bool(GROQ_API_KEY)

# Try local LLaMA only if Groq is not configured
llm = None
if not USE_GROQ:
    BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "llama.gguf")
    if os.path.exists(MODEL_PATH):
        try:
            from llama_cpp import Llama
            llm = Llama(
                model_path=MODEL_PATH,
                n_ctx=1024,
                n_threads=6,
                n_batch=32,
                verbose=False
            )
            print("[LLaMA] Local model loaded.")
        except Exception as e:
            print(f"[LLaMA] Failed to load local model: {e}")
    else:
        print("[LLaMA] No local model found at expected path.")
        print("[LLaMA] Set GROQ_API_KEY in .env for cloud inference.")


# =========================================================
# DYNAMIC SEVERITY SCORING
# Maps claim + evidence text to per-dimension impact scores
# =========================================================

SEVERITY_KEYWORDS = {
    "economic": [
        "economy", "gdp", "inflation", "tax", "budget", "rupee", "market",
        "price", "trade", "employment", "jobs", "income", "poverty",
        "financial", "bank", "investment", "subsidy", "currency", "growth",
        "recession", "fiscal", "revenue", "debt", "loan", "export", "import"
    ],
    "social": [
        "caste", "religion", "minority", "community", "protest", "riot",
        "gender", "education", "health", "discrimination", "rights",
        "farmer", "student", "women", "youth", "violence", "mob",
        "reservation", "welfare", "poverty", "inequality", "justice"
    ],
    "political": [
        "election", "vote", "party", "government", "minister", "parliament",
        "bjp", "congress", "opposition", "policy", "law", "bill", "court",
        "constitution", "modi", "rahul", "chief minister", "lok sabha",
        "rajya sabha", "democracy", "corruption", "scandal", "rally"
    ],
    "national": [
        "india", "pakistan", "china", "border", "army", "military",
        "national", "security", "terrorism", "kashmir", "defence",
        "sovereignty", "nuclear", "diplomatic", "foreign", "attack",
        "war", "soldier", "air force", "navy", "intelligence"
    ]
}


def compute_severity(claim: str, evidence_texts: list) -> dict:
    """
    Compute dynamic severity scores from claim and evidence keywords.

    Each dimension scored 0-100:
      - Baseline of 5 (every claim has some minimal potential)
      - Each keyword hit adds proportional weight
      - Capped at 100

    This replaces the hardcoded {economic:40, social:60, political:70, national:30}
    placeholder that never changed regardless of the claim.
    """
    combined = (claim + " " + " ".join(evidence_texts)).lower()

    scores = {}
    for dimension, keywords in SEVERITY_KEYWORDS.items():
        hits    = sum(1 for kw in keywords if kw in combined)
        max_kws = len(keywords)
        # Scale: 0 hits → 5 (baseline), all keywords → 95, capped at 100
        score   = min(100, int(5 + (hits / max_kws) * 90))
        scores[dimension] = score

    return scores


# =========================================================
# GROQ CLOUD INFERENCE (LLaMA-3.1 8B)
# =========================================================

def _run_groq(prompt: str) -> str:
    """Call Groq API (free tier) with LLaMA-3.1-8B-Instant model."""
    try:
        from groq import Groq
        client   = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq] API error: {e}")
        return ""


# =========================================================
# LOCAL LLAMA INFERENCE
# =========================================================

def _run_local(prompt: str) -> str:
    """Run inference using local llama.gguf model."""
    if llm is None:
        return ""
    try:
        output = llm(
            prompt,
            max_tokens=120,
            temperature=0.2,
            stop=["\n\n"]
        )
        return output["choices"][0]["text"].strip()
    except Exception as e:
        print(f"[LLaMA Local] Inference error: {e}")
        return ""


# =========================================================
# PUBLIC INTERFACE — called by analyzer.py
# =========================================================

def llama_reason(claim: str, evidence: list) -> dict:
    """
    Generate a fact-checking explanation for the given claim.

    Priority:
    1. Groq API (LLaMA-3.1-8B) if GROQ_API_KEY is set in .env
    2. Local llama.gguf if file exists
    3. Hardcoded fallback message

    Severity is now computed dynamically from claim + evidence keywords,
    replacing the hardcoded {40, 60, 70, 30} placeholder.

    Indian source count is computed from URL domain matching.
    """
    evidence_texts      = []
    evidence_text_block = ""

    for i, e in enumerate(evidence[:3]):
        title   = e.get("title", "")
        snippet = e.get("content", "")[:200]
        line    = f"{i+1}. {title} — {snippet}"
        evidence_text_block += line + "\n"
        evidence_texts.append(title + " " + snippet)

    prompt = f"""You are an AI fact-checking assistant for Indian news claims.

Claim:
{claim}

Evidence from sources:
{evidence_text_block}

Instructions:
1. Compare the claim with the evidence provided.
2. Determine if the evidence supports, contradicts, or partially supports the claim.
3. Write a concise explanation referencing the evidence.

Return EXACTLY in this format:
Verdict: TRUE / FALSE / MISLEADING
Confidence: HIGH / MEDIUM / LOW
Reason: 2-3 sentence explanation referencing the evidence."""

    # Choose inference backend — Groq preferred, local fallback
    if USE_GROQ:
        reasoning = _run_groq(prompt)
    else:
        reasoning = _run_local(prompt)

    # Fallback if both backends fail
    if not reasoning:
        reasoning = (
            "Verdict: MISLEADING\n"
            "Confidence: LOW\n"
            "Reason: Automated analysis could not generate a detailed explanation. "
            "Please review the evidence sources manually."
        )

    # Parse verdict for source counting
    reasoning_upper = reasoning.upper()
    supporting = 0
    refuting   = 0

    if "VERDICT: TRUE" in reasoning_upper:
        supporting = min(len(evidence), 3)
    elif "VERDICT: FALSE" in reasoning_upper:
        refuting = min(len(evidence), 3)
    else:
        # MISLEADING — split evenly
        supporting = len(evidence) // 2
        refuting   = len(evidence) - supporting

    # Dynamic severity from claim + evidence keywords
    severity = compute_severity(claim, evidence_texts)

    # Count Indian vs global sources by domain
    indian_domains = [
        "ndtv", "thehindu", "timesofindia", "hindustantimes",
        "indianexpress", "india", "scroll.in", "wire.in",
        "livemint", "deccanherald"
    ]
    indian_count = sum(
        1 for e in evidence
        if any(d in e.get("url", "").lower() for d in indian_domains)
    )

    return {
        "summary":            reasoning,
        "supporting_sources": supporting,
        "refuting_sources":   refuting,
        "evidence":           evidence,
        "confidence":         0.6,
        "prediction":         (
            "true"  if supporting > refuting  else
            "false" if refuting  > supporting else
            "mixed"
        ),
        "evidence_strength":  0.5,
        "indian_sources":     indian_count,
        "global_sources":     len(evidence),
        "severity":           severity,
    }