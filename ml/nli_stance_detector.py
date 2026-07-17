# backend/ml/nli_stance_detector.py
# Replaces keyword-based direction scoring in HybridFact
# Uses DeBERTa-v3-base-mnli-fever-anli — pretrained on FEVER itself
# Install: pip install transformers torch

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Dict, Optional

# Best model for FEVER-style fact verification
# Trained on MNLI + FEVER + ANLI — directly relevant to your task
NLI_MODEL_NAME = "cross-encoder/nli-deberta-v3-base"

# Alternative lighter model if memory is constrained:
# NLI_MODEL_NAME = "typeform/distilbert-base-uncased-mnli"

_tokenizer = None
_model = None
_device = None


def _load_model():
    global _tokenizer, _model, _device
    if _model is None:
        print(f"[NLI] Loading model: {NLI_MODEL_NAME}")
        _tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL_NAME)
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _model = _model.to(_device)
        _model.eval()
        print(f"[NLI] Model loaded on {_device}")
    return _tokenizer, _model, _device


def get_stance_score(claim: str, evidence_text: str) -> Dict:
    """
    Compute NLI-based stance of evidence toward claim.

    Returns:
        dict with keys:
            direction: +1 (supports), -1 (refutes), 0 (neutral)
            entailment_prob: float 0-1
            contradiction_prob: float 0-1
            neutral_prob: float 0-1
            confidence: max probability
            label: "SUPPORTS" | "REFUTES" | "NEUTRAL"
    """
    tokenizer, model, device = _load_model()

    # NLI format: premise = evidence, hypothesis = claim
    # (evidence either entails or contradicts the claim)
    inputs = tokenizer(
        evidence_text[:512],   # truncate evidence to fit context
        claim[:256],           # claim as hypothesis
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

    # DeBERTa NLI label order: [entailment, neutral, contradiction]
    # cross-encoder/nli-deberta-v3-base uses: contradiction=0, neutral=1, entailment=2
    label_map = model.config.id2label

    # Safely map regardless of model's label ordering
    entailment_prob = 0.0
    contradiction_prob = 0.0
    neutral_prob = 0.0

    for idx, prob in enumerate(probs):
        label = label_map[idx].lower()
        if "entail" in label:
            entailment_prob = float(prob)
        elif "contradict" in label:
            contradiction_prob = float(prob)
        else:
            neutral_prob = float(prob)

    # Direction decision with minimum confidence threshold
    CONFIDENCE_THRESHOLD = 0.50  # only assign direction if confident enough

    if entailment_prob >= CONFIDENCE_THRESHOLD and entailment_prob > contradiction_prob:
        direction = 1
        label = "SUPPORTS"
    elif contradiction_prob >= CONFIDENCE_THRESHOLD and contradiction_prob > entailment_prob:
        direction = -1
        label = "REFUTES"
    else:
        direction = 0
        label = "NEUTRAL"

    return {
        "direction": direction,
        "entailment_prob": entailment_prob,
        "contradiction_prob": contradiction_prob,
        "neutral_prob": neutral_prob,
        "confidence": float(max(probs)),
        "label": label
    }


def compute_nli_signal(
    claim: str,
    evidence_list: List[Dict],
    sim_threshold: float = 0.25
) -> Dict:
    """
    Replacement for the keyword-based directional signal fusion in HybridFact.
    Computes weighted NLI signal across all retrieved evidence articles.

    Args:
        claim: The claim being verified
        evidence_list: List of dicts with keys: text, similarity, credibility

    Returns:
        dict with:
            signal: float in [-1, +1]
            num_supporting: int
            num_refuting: int
            num_neutral: int
            evidence_details: list of per-article results
    """
    if not evidence_list:
        return {
            "signal": 0.0,
            "num_supporting": 0,
            "num_refuting": 0,
            "num_neutral": 0,
            "evidence_details": []
        }

    weighted_scores = []
    evidence_details = []
    num_supporting = 0
    num_refuting = 0
    num_neutral = 0

    for ev in evidence_list:
        sim = ev.get("similarity", 0.0)
        cred = ev.get("credibility", 0.5)
        text = ev.get("text", "")

        if sim < sim_threshold or not text.strip():
            continue

        stance = get_stance_score(claim, text)

        # Weighted contribution: similarity × credibility × direction
        weight = sim * cred
        weighted_contribution = weight * stance["direction"]
        weighted_scores.append(weighted_contribution)

        if stance["direction"] == 1:
            num_supporting += 1
        elif stance["direction"] == -1:
            num_refuting += 1
        else:
            num_neutral += 1

        evidence_details.append({
            "text_preview": text[:100],
            "similarity": sim,
            "credibility": cred,
            "stance": stance
        })

    if not weighted_scores:
        signal = 0.0
    else:
        signal = float(np.mean(weighted_scores))
        # Clip to [-1, +1]
        signal = max(-1.0, min(1.0, signal))

    return {
        "signal": signal,
        "num_supporting": num_supporting,
        "num_refuting": num_refuting,
        "num_neutral": num_neutral,
        "evidence_details": evidence_details
    }


def compare_keyword_vs_nli(
    claim: str,
    evidence_text: str,
    keyword_direction: int
) -> Dict:
    """
    Utility to compare old keyword method vs new NLI method.
    Useful for generating Table in paper showing improvement.
    """
    nli_result = get_stance_score(claim, evidence_text)

    return {
        "claim": claim,
        "keyword_direction": keyword_direction,
        "nli_direction": nli_result["direction"],
        "agreement": keyword_direction == nli_result["direction"],
        "nli_confidence": nli_result["confidence"],
        "nli_label": nli_result["label"],
        "entailment_prob": nli_result["entailment_prob"],
        "contradiction_prob": nli_result["contradiction_prob"],
        "neutral_prob": nli_result["neutral_prob"]
    }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        {
            "claim": "Marie Curie was born in Warsaw",
            "evidence": "Marie Curie was born on 7 November 1867 in Warsaw, in the Kingdom of Poland.",
            "expected": "SUPPORTS"
        },
        {
            "claim": "The Eiffel Tower is located in Berlin",
            "evidence": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.",
            "expected": "REFUTES"
        },
        {
            "claim": "Magic Johnson played for the Lakers",
            "evidence": "Earvin Magic Johnson Jr. played point guard for the Los Angeles Lakers of the NBA.",
            "expected": "SUPPORTS"
        },
        {
            "claim": "Aristotle was a student of Plato",
            "evidence": "Aristotle was an ancient Greek philosopher. He studied at Plato's Academy in Athens.",
            "expected": "SUPPORTS"
        }
    ]

    print("NLI Stance Detection Test")
    print("=" * 60)
    for tc in test_cases:
        result = get_stance_score(tc["claim"], tc["evidence"])
        status = "PASS" if result["label"] == tc["expected"] else "FAIL"
        print(f"\n[{status}] Claim   : {tc['claim']}")
        print(f"       Evidence: {tc['evidence'][:80]}...")
        print(f"       Expected: {tc['expected']}  Got: {result['label']}")
        print(f"       Probs — Entail: {result['entailment_prob']:.3f} | "
              f"Contradict: {result['contradiction_prob']:.3f} | "
              f"Neutral: {result['neutral_prob']:.3f}")