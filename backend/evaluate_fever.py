# evaluate_fever.py — place in D:\pulseindia-main\backend\
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import json
from sklearn.metrics import accuracy_score, classification_report

from app.services.analyzer import analyze_claim, predict_claim

# ── Load and clean FEVER data ────────────────────────────
DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "ml", "data", "fever_eval_300.json"
)

with open(DATA_PATH) as f:
    data = json.load(f)

# Drop uncertain — keep only binary true/false
data = [d for d in data if d["label"] in ["true", "false"]]
print(f"Evaluating on {len(data)} binary FEVER samples\n")

true_labels    = []
baseline_preds = []
hybrid_preds   = []

wiki_hits      = 0
tavily_hits    = 0
overrides      = 0

for i, sample in enumerate(data):
    claim = sample["claim"]
    label = sample["label"]

    # ── Baseline ──────────────────────────────────────────
    base_pred, _ = predict_claim(claim)
    if base_pred == "mixed":
        base_pred = "false"  # conservative mapping for binary task

    # ── Hybrid ────────────────────────────────────────────
    result      = analyze_claim(claim)
    hybrid_pred = result["prediction"]
    if hybrid_pred == "mixed":
        hybrid_pred = "false"  # same conservative mapping

    true_labels.append(label)
    baseline_preds.append(base_pred)
    hybrid_preds.append(hybrid_pred)

    if result.get("wiki_found"):
        wiki_hits += 1
    if result.get("tavily_found"):
        tavily_hits += 1
    if result.get("override_triggered"):
        overrides += 1

    # Progress every 10 samples
    if (i + 1) % 10 == 0:
        b_acc = sum(t == p for t, p in zip(true_labels, baseline_preds)) / len(true_labels)
        h_acc = sum(t == p for t, p in zip(true_labels, hybrid_preds))   / len(true_labels)
        print(f"[{i+1:3d}/{len(data)}] "
              f"Baseline: {b_acc:.3f} | Hybrid: {h_acc:.3f} | "
              f"Wiki: {wiki_hits} | Tavily: {tavily_hits} | "
              f"Overrides: {overrides}")

# ── Final Results ─────────────────────────────────────────
print("\n" + "=" * 55)
print("BASELINE RESULTS (DistilBERT only)")
print("=" * 55)
b_acc = accuracy_score(true_labels, baseline_preds)
print(f"Accuracy : {b_acc:.4f}")
print(classification_report(true_labels, baseline_preds))

print("\n" + "=" * 55)
print("HYBRID RESULTS (Full pipeline)")
print("=" * 55)
h_acc = accuracy_score(true_labels, hybrid_preds)
print(f"Accuracy : {h_acc:.4f}")
print(classification_report(true_labels, hybrid_preds))

print("\n" + "=" * 55)
print("IMPROVEMENT SUMMARY")
print("=" * 55)
print(f"Baseline accuracy  : {b_acc:.4f}")
print(f"Hybrid accuracy    : {h_acc:.4f}")
print(f"Improvement        : {h_acc - b_acc:+.4f}")
print(f"Wikipedia hits     : {wiki_hits}/{len(data)} "
      f"({100*wiki_hits/len(data):.1f}%)")
print(f"Tavily hits        : {tavily_hits}/{len(data)} "
      f"({100*tavily_hits/len(data):.1f}%)")
print(f"Overrides fired    : {overrides}/{len(data)} "
      f"({100*overrides/len(data):.1f}%)")