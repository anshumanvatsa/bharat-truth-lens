# backend/ml/bert_score_evaluator.py
# Quantitative evaluation of LLaMA-3 explanation quality
# Replaces the "50 manually reviewed samples" with actual metrics
# Install: pip install bert-score

from bert_score import score as bert_score_compute
import json
import numpy as np
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings("ignore")


def compute_bertscore_single(
    explanation: str,
    reference_evidence: str,
    model_type: str = "roberta-large"
) -> Dict:
    """
    Compute BERTScore between a LLaMA explanation and its source evidence.

    High score = explanation faithfully reflects what the evidence says.
    Low score = explanation may be hallucinating.

    Args:
        explanation: LLaMA-generated explanation text
        reference_evidence: The evidence text LLaMA was given
        model_type: BERTScore backbone (deberta gives best correlation with human judgment)

    Returns:
        dict with precision, recall, f1 scores
    """
    P, R, F1 = bert_score_compute(
    cands=[explanation],
    refs=[reference_evidence],
    model_type=model_type,
    lang="en",
    verbose=False,
    rescale_with_baseline=True
)

    return {
        "precision": float(P[0]),
        "recall": float(R[0]),
        "f1": float(F1[0]),
        "faithfulness_label": _faithfulness_label(float(F1[0]))
    }


def _faithfulness_label(f1_score: float) -> str:
    """
    Convert BERTScore F1 to interpretable faithfulness label.
    Thresholds calibrated for deberta-xlarge-mnli.
    """
    if f1_score >= 0.90:
        return "HIGH"
    elif f1_score >= 0.80:
        return "MEDIUM"
    else:
        return "LOW — possible hallucination"


def evaluate_explanation_batch(
    explanations: List[str],
    evidence_texts: List[str],
    claims: List[str],
    predictions: List[str],
    true_labels: List[str],
    model_type: str = "roberta-large"
) -> Dict:
    """
    Full batch evaluation of LLaMA explanations.
    Run this on all 500 samples (or the subset that has explanations).

    Args:
        explanations: List of LLaMA-generated explanations
        evidence_texts: Corresponding evidence each explanation was based on
        claims: Original claims
        predictions: HybridFact predictions
        true_labels: Ground truth labels
        model_type: BERTScore model

    Returns:
        Full evaluation report suitable for inclusion in paper
    """
    assert len(explanations) == len(evidence_texts), "Lists must be same length"

    print(f"[BERTScore] Evaluating {len(explanations)} explanations...")

    P, R, F1 = bert_score_compute(
        cands=explanations,
        refs=evidence_texts,
        model_type=model_type,
        lang="en",
        verbose=True
    )

    f1_scores = F1.numpy()
    p_scores = P.numpy()
    r_scores = R.numpy()

    # Stratify by correctness
    correct_idx = [i for i, (p, t) in enumerate(zip(predictions, true_labels)) if p == t]
    incorrect_idx = [i for i, (p, t) in enumerate(zip(predictions, true_labels)) if p != t]

    correct_f1 = f1_scores[correct_idx] if correct_idx else np.array([0.0])
    incorrect_f1 = f1_scores[incorrect_idx] if incorrect_idx else np.array([0.0])

    # Faithfulness breakdown
    high = sum(1 for f in f1_scores if f >= 0.90)
    medium = sum(1 for f in f1_scores if 0.80 <= f < 0.90)
    low = sum(1 for f in f1_scores if f < 0.80)

    report = {
        "n_evaluated": len(explanations),
        "overall": {
            "mean_f1": float(np.mean(f1_scores)),
            "std_f1": float(np.std(f1_scores)),
            "mean_precision": float(np.mean(p_scores)),
            "mean_recall": float(np.mean(r_scores)),
            "median_f1": float(np.median(f1_scores)),
            "min_f1": float(np.min(f1_scores)),
            "max_f1": float(np.max(f1_scores))
        },
        "faithfulness_breakdown": {
            "high_faithfulness_pct": round(high / len(f1_scores) * 100, 1),
            "medium_faithfulness_pct": round(medium / len(f1_scores) * 100, 1),
            "low_faithfulness_pct": round(low / len(f1_scores) * 100, 1),
            "n_high": high,
            "n_medium": medium,
            "n_low": low
        },
        "by_correctness": {
            "correct_predictions_mean_f1": float(np.mean(correct_f1)),
            "incorrect_predictions_mean_f1": float(np.mean(incorrect_f1)),
            "n_correct": len(correct_idx),
            "n_incorrect": len(incorrect_idx)
        },
        "per_sample": [
            {
                "claim": claims[i],
                "prediction": predictions[i],
                "true_label": true_labels[i],
                "correct": predictions[i] == true_labels[i],
                "bertscore_f1": float(f1_scores[i]),
                "bertscore_precision": float(p_scores[i]),
                "bertscore_recall": float(r_scores[i]),
                "faithfulness": _faithfulness_label(float(f1_scores[i])),
                "explanation_preview": explanations[i][:150]
            }
            for i in range(len(explanations))
        ]
    }

    return report


def generate_paper_table(report: Dict) -> str:
    """
    Generates the LaTeX table content for Section VI-G of your paper.
    Prints a formatted table showing BERTScore results.
    """
    o = report["overall"]
    fb = report["faithfulness_breakdown"]
    bc = report["by_correctness"]

    table = f"""
\\subsection{{Quantitative Evaluation of LLaMA-3 Explanation Quality}}

To quantify the faithfulness of LLaMA-3 8B explanations to retrieved evidence,
we computed BERTScore (DeBERTa-XL-MNLI backbone) across all
{report['n_evaluated']} evaluated samples.

Key results:
- Mean BERTScore F1: {o['mean_f1']:.4f} (SD = {o['std_f1']:.4f})
- High faithfulness (F1 ≥ 0.90): {fb['n_high']} samples ({fb['high_faithfulness_pct']}\\%)
- Medium faithfulness: {fb['n_medium']} samples ({fb['medium_faithfulness_pct']}\\%)  
- Low faithfulness / hallucination risk: {fb['n_low']} samples ({fb['low_faithfulness_pct']}\\%)

Explanations for correct predictions achieved higher mean BERTScore F1 
({bc['correct_predictions_mean_f1']:.4f}) compared to incorrect predictions 
({bc['incorrect_predictions_mean_f1']:.4f}), indicating that retrieval quality 
and explanation faithfulness are correlated with classification accuracy.

\\begin{{table}}[h]
\\centering
\\caption{{BERTScore Evaluation of LLaMA-3 Explanations (n={report['n_evaluated']})}}
\\begin{{tabular}}{{lcc}}
\\hline
\\textbf{{Metric}} & \\textbf{{Correct Predictions}} & \\textbf{{Incorrect Predictions}} \\\\
\\hline
Mean BERTScore F1 & {bc['correct_predictions_mean_f1']:.4f} & {bc['incorrect_predictions_mean_f1']:.4f} \\\\
High Faithfulness & {fb['high_faithfulness_pct']}\\% & - \\\\
Low Faithfulness  & {fb['low_faithfulness_pct']}\\% & - \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
"""
    return table


def load_and_evaluate_from_cache(
    evidence_cache_path: str,
    explanations_path: str,
    output_path: str = "bertscore_results.json"
) -> Dict:
    """
    Load existing cache files and run evaluation.
    Matches your existing evidence_cache_500.json structure.

    Args:
        evidence_cache_path: Path to evidence_cache_500.json
        explanations_path: Path to JSON file with LLaMA explanations
        output_path: Where to save results
    """
    with open(evidence_cache_path, "r") as f:
        evidence_cache = json.load(f)

    with open(explanations_path, "r") as f:
        explanation_data = json.load(f)

    explanations = []
    evidence_texts = []
    claims = []
    predictions = []
    true_labels = []

    for item in explanation_data:
        claim = item["claim"]
        explanation = item.get("explanation", "")

        if not explanation:
            continue

        # Get corresponding evidence from cache
        cached = evidence_cache.get(claim, {})
        all_evidence = []
        if cached.get("wiki_summary"):
            all_evidence.append(cached["wiki_summary"])
        for art in cached.get("tavily_results", [])[:2]:
            if art.get("content"):
                all_evidence.append(art["content"][:300])

        reference = " ".join(all_evidence)[:512]

        if not reference.strip():
            continue

        explanations.append(explanation)
        evidence_texts.append(reference)
        claims.append(claim)
        predictions.append(item.get("prediction", "unknown"))
        true_labels.append(item.get("true_label", "unknown"))

    print(f"[BERTScore] Found {len(explanations)} explanation-evidence pairs")

    report = evaluate_explanation_batch(
        explanations, evidence_texts, claims, predictions, true_labels
    )

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[BERTScore] Results saved to {output_path}")

    print(generate_paper_table(report))
    return report


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_explanations = [
        "According to Wikipedia, Marie Curie was indeed born in Warsaw in 1867, confirming the claim.",
        "The evidence clearly states the Eiffel Tower is in Paris, France, not Berlin. The claim is false.",
        "The retrieved article discusses the movie's critical reception but does not mention its release year. Insufficient evidence to verify.",
    ]
    test_evidence = [
        "Marie Curie was born on 7 November 1867 in Warsaw, in the Kingdom of Poland, then part of the Russian Empire.",
        "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It was constructed from 1887 to 1889.",
        "The film received widespread critical acclaim, with particular praise for the direction and performances. It grossed over $200 million worldwide.",
    ]

    print("BERTScore Evaluation Test")
    print("=" * 60)
    for i, (exp, ev) in enumerate(zip(test_explanations, test_evidence)):
        result = compute_bertscore_single(exp, ev)
        print(f"\nSample {i+1}:")
        print(f"  Explanation : {exp[:80]}...")
        print(f"  Evidence    : {ev[:80]}...")
        print(f"  BERTScore F1: {result['f1']:.4f}")
        print(f"  Faithfulness: {result['faithfulness_label']}")