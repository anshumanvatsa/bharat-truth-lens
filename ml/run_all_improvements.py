# backend/ml/run_all_improvements.py
# Master script to run all 4 improvements in order
# Run this once after placing all files in backend/ml/
# 
# Prerequisites (run in terminal):
#   pip install spacy bert-score transformers torch scipy scikit-learn
#   python -m spacy download en_core_web_lg

import json
import os
import sys
from pathlib import Path

# ── Step 1: SpaCy NER — test extraction on your FEVER claims ─────────────────
def run_ner_evaluation(fever_data_path: str, output_path: str = "ner_comparison.json"):
    """
    Compare old rule-based extractor vs new SpaCy NER on your FEVER claims.
    Generates Table showing improvement in entity extraction accuracy.
    """
    print("\n" + "="*60)
    print("STEP 1: SpaCy NER Extractor Evaluation")
    print("="*60)

    from spacy_ner_extractor import extract_entity_spacy, extract_entity_with_fallback_info
    # Original rule-based extractor (copy from your existing code)
    import re

    def rule_based_extractor(claim: str) -> str:
        normalized = claim.lower()
        for article in ["the ", "a ", "an "]:
            if normalized.startswith(article):
                normalized = normalized[len(article):]
        tokens = claim.split()
        entity_tokens = []
        for token in tokens:
            clean = re.sub(r"[^a-zA-Z0-9\s]", "", token)
            if clean and (clean[0].isupper() or entity_tokens):
                entity_tokens.append(clean)
                if len(entity_tokens) >= 3:
                    break
            elif entity_tokens:
                break
        return " ".join(entity_tokens) if entity_tokens else " ".join(claim.split()[:3])

    with open(fever_data_path, "r") as f:
        fever_data = json.load(f)

    # Use the first 100 samples for quick comparison
    sample = fever_data[:100] if len(fever_data) > 100 else fever_data

    results = []
    rule_failures = 0
    spacy_improvements = 0

    for item in sample:
        claim = item.get("claim", "")
        if not claim:
            continue

        rule_entity = rule_based_extractor(claim)
        spacy_info = extract_entity_with_fallback_info(claim)
        spacy_entity = spacy_info["entity"]

        # Flag cases where spaCy clearly does better
        # (rule-based grabs "According" or similar non-entity words)
        bad_rule_words = ["according", "the", "a", "an", "this", "that", "it", "he", "she"]
        rule_failed = rule_entity.lower().split()[0] in bad_rule_words if rule_entity else True

        if rule_failed:
            rule_failures += 1
            if spacy_entity and spacy_entity.lower().split()[0] not in bad_rule_words:
                spacy_improvements += 1

        results.append({
            "claim": claim,
            "rule_based": rule_entity,
            "spacy": spacy_entity,
            "spacy_method": spacy_info["method"],
            "spacy_entity_type": spacy_info["entity_type"],
            "rule_likely_failed": rule_failed
        })

    summary = {
        "total_evaluated": len(results),
        "rule_based_likely_failures": rule_failures,
        "spacy_improvements_on_failures": spacy_improvements,
        "estimated_improvement_pct": round(spacy_improvements / max(rule_failures, 1) * 100, 1),
        "samples": results[:20]  # save first 20 for inspection
    }

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"  Rule-based failures detected: {rule_failures}/{len(results)}")
    print(f"  SpaCy improvements on those: {spacy_improvements}")
    print(f"  Estimated improvement: {summary['estimated_improvement_pct']}%")
    print(f"  Results saved to: {output_path}")
    return summary


# ── Step 2: Bootstrap CI ──────────────────────────────────────────────────────
def run_bootstrap(
    ablation_results_path: str = "ablation_results.json",
    output_path: str = "bootstrap_results.json"
):
    print("\n" + "="*60)
    print("STEP 2: Bootstrap Confidence Intervals")
    print("="*60)

    from bootstrap_ci import run_from_ablation_results
    report = run_from_ablation_results(
        ablation_results_path=ablation_results_path,
        output_path=output_path,
        n_iterations=10000
    )

    ci = report["bootstrap_ci"]
    print(f"\n  95% CI for delta Macro F1: [{ci['delta_macro_f1_ci'][0]*100:+.2f}, {ci['delta_macro_f1_ci'][1]*100:+.2f}] pts")
    print(f"  Zero excluded: {ci['zero_excluded_macro_f1']} ← this is what you put in the paper")
    print(f"  95% CI for delta F1-True: [{ci['delta_f1_true_ci'][0]*100:+.2f}, {ci['delta_f1_true_ci'][1]*100:+.2f}] pts")
    return report


# ── Step 3: BERTScore for LLaMA explanations ─────────────────────────────────
def run_bertscore(
    evidence_cache_path: str = "evidence_cache_500.json",
    explanations_path: str = "llama_explanations.json",
    output_path: str = "bertscore_results.json"
):
    print("\n" + "="*60)
    print("STEP 3: BERTScore — LLaMA Explanation Quality")
    print("="*60)

    if not os.path.exists(explanations_path):
        print(f"  [SKIP] {explanations_path} not found.")
        print("  To generate explanations file, run:")
        print("  python generate_llama_explanations.py")
        print("  (see generate_llama_explanations.py for format)")
        return None

    from bert_score_evaluator import load_and_evaluate_from_cache
    report = load_and_evaluate_from_cache(
        evidence_cache_path=evidence_cache_path,
        explanations_path=explanations_path,
        output_path=output_path
    )

    o = report["overall"]
    print(f"\n  Mean BERTScore F1: {o['mean_f1']:.4f}")
    print(f"  High faithfulness: {report['faithfulness_breakdown']['high_faithfulness_pct']}%")
    print(f"  Low faithfulness (hallucination risk): {report['faithfulness_breakdown']['low_faithfulness_pct']}%")
    return report


# ── Step 4: NLI Stance Detection ─────────────────────────────────────────────
def run_nli_comparison(
    evidence_cache_path: str = "evidence_cache_500.json",
    ablation_results_path: str = "ablation_results.json",
    output_path: str = "nli_comparison_results.json",
    n_samples: int = 100  # start with 100 to test, then increase
):
    """
    Runs NLI stance detection and compares with keyword method.
    Note: NLI inference is slower (~1-2s per sample on CPU).
    For 500 samples expect ~10-15 minutes on CPU.
    """
    print("\n" + "="*60)
    print("STEP 4: NLI Stance Detection vs Keyword Method")
    print("="*60)
    print(f"  Running on {n_samples} samples (increase n_samples for full run)")

    from nli_stance_detector import get_stance_score, compare_keyword_vs_nli

    with open(evidence_cache_path, "r") as f:
        evidence_cache = json.load(f)

    with open(ablation_results_path, "r") as f:
        ablation = json.load(f)

    claims = ablation.get("claims", [])[:n_samples]
    keyword_directions = ablation.get("keyword_directions", [None] * len(claims))[:n_samples]
    true_labels = ablation.get("true_labels", [])[:n_samples]

    results = []
    agreements = 0
    nli_correct = 0
    keyword_correct = 0

    for i, claim in enumerate(claims):
        cached = evidence_cache.get(claim, {})
        wiki = cached.get("wiki_summary", "")
        tavily_texts = [a.get("content", "") for a in cached.get("tavily_results", [])[:1]]
        evidence = wiki if wiki else (tavily_texts[0] if tavily_texts else "")

        if not evidence:
            continue

        kw_dir = keyword_directions[i] if keyword_directions[i] is not None else 0
        true_label = true_labels[i] if i < len(true_labels) else None

        comparison = compare_keyword_vs_nli(claim, evidence, kw_dir)

        if comparison["agreement"]:
            agreements += 1

        # Check which method is "more correct" (direction toward truth)
        if true_label is not None:
            expected_direction = 1 if true_label == 1 else -1
            if comparison["nli_direction"] == expected_direction:
                nli_correct += 1
            if comparison["keyword_direction"] == expected_direction:
                keyword_correct += 1

        results.append(comparison)
        if (i + 1) % 20 == 0:
            print(f"  Processed {i+1}/{n_samples} claims...")

    n_valid = len(results)
    summary = {
        "n_processed": n_valid,
        "agreement_rate": round(agreements / max(n_valid, 1), 3),
        "nli_directional_accuracy": round(nli_correct / max(n_valid, 1), 3),
        "keyword_directional_accuracy": round(keyword_correct / max(n_valid, 1), 3),
        "nli_improvement": round((nli_correct - keyword_correct) / max(n_valid, 1), 3),
        "samples": results[:20]
    }

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Agreement between NLI and keyword: {summary['agreement_rate']*100:.1f}%")
    print(f"  Keyword directional accuracy: {summary['keyword_directional_accuracy']*100:.1f}%")
    print(f"  NLI directional accuracy:     {summary['nli_directional_accuracy']*100:.1f}%")
    print(f"  NLI improvement over keywords: {summary['nli_improvement']*100:+.1f}%")
    print(f"  Results saved to: {output_path}")
    return summary


# ── Helper: Generate LLaMA explanations file if missing ──────────────────────
def generate_explanations_template():
    """Shows the expected format for llama_explanations.json"""
    template = [
        {
            "claim": "Marie Curie was born in Warsaw",
            "explanation": "According to Wikipedia, Marie Curie was born on 7 November 1867 in Warsaw...",
            "prediction": "true",
            "true_label": "true"
        }
    ]
    print("\nExpected format for llama_explanations.json:")
    print(json.dumps(template, indent=2))
    print("\nGenerate this by saving LLaMA outputs during evaluate_fever.py run")
    print("Add: json.dump(explanation_list, open('llama_explanations.json','w'))")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run all HybridFact improvements")
    parser.add_argument("--step", type=str, default="all",
                        choices=["all", "ner", "bootstrap", "bertscore", "nli"],
                        help="Which step to run")
    parser.add_argument("--fever-data", type=str, default="fever_dev.jsonl",
                        help="Path to FEVER data file")
    parser.add_argument("--ablation-results", type=str, default="ablation_results.json")
    parser.add_argument("--evidence-cache", type=str, default="evidence_cache_500.json")
    parser.add_argument("--explanations", type=str, default="llama_explanations.json")
    parser.add_argument("--nli-samples", type=int, default=100,
                        help="Number of samples for NLI comparison (full=500, slow)")
    args = parser.parse_args()

    # Check required files exist
    required_files = {
        "ablation_results.json": args.ablation_results,
        "evidence_cache_500.json": args.evidence_cache,
    }

    missing = [name for name, path in required_files.items() if not os.path.exists(path)]
    if missing:
        print(f"\n[ERROR] Missing required files: {missing}")
        print("These should already exist from your HybridFact evaluation runs.")
        print("Check paths and re-run.")
        sys.exit(1)

    print("\nHybridFact — Running All Improvements")
    print("="*60)

    if args.step in ("all", "ner"):
        if os.path.exists(args.fever_data):
            run_ner_evaluation(args.fever_data)
        else:
            print(f"[SKIP NER] {args.fever_data} not found — provide correct path")

    if args.step in ("all", "bootstrap"):
        run_bootstrap(args.ablation_results)

    if args.step in ("all", "bertscore"):
        run_bertscore(args.evidence_cache, args.explanations)

    if args.step in ("all", "nli"):
        run_nli_comparison(args.evidence_cache, args.ablation_results,
                           n_samples=args.nli_samples)

    print("\n" + "="*60)
    print("All steps complete. Check output JSON files for paper-ready numbers.")
    print("="*60)