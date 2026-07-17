# liar_eval.py
# Evaluates DistilBERT on LIAR dataset (6-class and binary)
# Generates all LIAR-specific figures for IEEE paper
# Place in D:\pulseindia-main\backend\
# Run: python liar_eval.py

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import csv
import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from transformers import DistilBertTokenizerFast
from transformers import DistilBertForSequenceClassification
from sklearn.metrics import (
    accuracy_score, f1_score,
    classification_report, confusion_matrix
)

# ── Model loading ─────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "models", "liar_model")

print("Loading DistilBERT model...")
tokenizer = DistilBertTokenizerFast.from_pretrained(
    MODEL_PATH, local_files_only=True)
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_PATH, local_files_only=True)
model.eval()
print("Model loaded.\n")

LABEL_NAMES = [
    "pants-fire", "false", "barely-true",
    "half-true", "mostly-true", "true"
]

OUTPUT_DIR = os.path.join(BASE_DIR, "..", "ml", "data", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":    "serif",
    "font.size":      11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi":     300,
})

# =========================================================
# PREDICTION
# =========================================================

def predict_6class(statement):
    """Returns raw 6-class label and confidence."""
    inputs = tokenizer(
        statement, return_tensors="pt",
        truncation=True, padding=True, max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
    probs    = torch.softmax(outputs.logits, dim=1)
    label_id = torch.argmax(probs).item()
    conf     = float(probs[0][label_id])
    return LABEL_NAMES[label_id], conf


def predict_binary(statement):
    """
    Maps 6-class output to binary true/false using
    probability mass approach for balanced predictions.
    """
    inputs = tokenizer(
        statement, return_tensors="pt",
        truncation=True, padding=True, max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)

    false_mass = float(probs[0][0] + probs[0][1])
    mixed_mass = float(probs[0][2] + probs[0][3])
    true_mass  = float(probs[0][4] + probs[0][5])

    if false_mass > true_mass and false_mass > mixed_mass:
        return "false", false_mass
    elif true_mass > false_mass and true_mass > mixed_mass:
        return "true", true_mass
    else:
        return "mixed", mixed_mass

# =========================================================
# LOAD LIAR TEST SET
# =========================================================

def load_liar(path):
    """Load LIAR TSV file. Columns: id, label, statement..."""
    samples = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            label     = row[1].strip()
            statement = row[2].strip()
            if label in LABEL_NAMES and statement:
                samples.append({
                    "statement": statement,
                    "label":     label
                })
    return samples

# Use the uploaded test set
TEST_PATH = os.path.join(
    BASE_DIR, "..", "ml", "data", "liar", "test.tsv"
)

# Fallback — check if files are in uploads or data folder
if not os.path.exists(TEST_PATH):
    # Try common alternative paths
    for alt in [
        os.path.join(BASE_DIR, "test.tsv"),
        os.path.join(BASE_DIR, "..", "ml", "data", "test.tsv"),
    ]:
        if os.path.exists(alt):
            TEST_PATH = alt
            break

print(f"Loading LIAR test set from: {TEST_PATH}")
test_data = load_liar(TEST_PATH)
print(f"Loaded {len(test_data)} test samples\n")

# =========================================================
# EVALUATION 1 — 6-CLASS
# =========================================================

print("="*55)
print("EVALUATION 1: 6-CLASS LIAR")
print("="*55)

true_6class = []
pred_6class = []

for i, sample in enumerate(test_data):
    pred, _ = predict_6class(sample["statement"])
    true_6class.append(sample["label"])
    pred_6class.append(pred)
    if (i + 1) % 100 == 0:
        print(f"  [{i+1}/{len(test_data)}] processed...")

acc_6  = accuracy_score(true_6class, pred_6class)
mf1_6  = f1_score(true_6class, pred_6class,
                   average="macro", zero_division=0)

print(f"\nAccuracy (6-class) : {acc_6:.4f}")
print(f"Macro F1  (6-class) : {mf1_6:.4f}")
print("\nClassification Report:")
print(classification_report(true_6class, pred_6class,
                             labels=LABEL_NAMES,
                             zero_division=0))

# =========================================================
# EVALUATION 2 — BINARY (true vs false, drop middle labels)
# =========================================================

print("="*55)
print("EVALUATION 2: BINARY LIAR (true/false only)")
print("="*55)

binary_data = [
    s for s in test_data
    if s["label"] in ["true", "mostly-true", "false", "pants-fire"]
]

# Map to binary
def to_binary_label(label):
    if label in ["true", "mostly-true"]:
        return "true"
    else:
        return "false"

true_binary = []
pred_binary = []

for i, sample in enumerate(binary_data):
    pred, _ = predict_binary(sample["statement"])
    if pred == "mixed":
        pred = "false"  # conservative mapping

    true_binary.append(to_binary_label(sample["label"]))
    pred_binary.append(pred)

    if (i + 1) % 100 == 0:
        print(f"  [{i+1}/{len(binary_data)}] processed...")

acc_bin = accuracy_score(true_binary, pred_binary)
mf1_bin = f1_score(true_binary, pred_binary,
                    average="macro", zero_division=0)

print(f"\nBinary samples     : {len(binary_data)}")
print(f"True  samples      : {sum(1 for l in true_binary if l == 'true')}")
print(f"False samples      : {sum(1 for l in true_binary if l == 'false')}")
print(f"\nAccuracy (binary)  : {acc_bin:.4f}")
print(f"Macro F1  (binary) : {mf1_bin:.4f}")
print("\nClassification Report:")
print(classification_report(true_binary, pred_binary,
                             zero_division=0))

# =========================================================
# FIGURE L1 — 6-Class Label Distribution + Accuracy
# =========================================================

print("\nGenerating figures...")

# Count predictions per class
from collections import Counter
true_counts = Counter(true_6class)
pred_counts = Counter(pred_6class)

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# L1a — True label distribution
ax = axes[0]
counts = [true_counts.get(l, 0) for l in LABEL_NAMES]
colors_dist = ["#F44336", "#FF5722", "#FF9800",
               "#FFC107", "#8BC34A", "#4CAF50"]
bars = ax.bar(LABEL_NAMES, counts, color=colors_dist,
              alpha=0.85, edgecolor="white", linewidth=0.5)
for bar, c in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 5, str(c),
            ha="center", va="bottom", fontsize=8,
            fontweight="bold")
ax.set_title("True Label Distribution\n(LIAR Test Set)")
ax.set_xlabel("Label")
ax.set_ylabel("Count")
ax.set_xticklabels(LABEL_NAMES, rotation=30, ha="right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)

# L1b — Per-class accuracy
ax = axes[1]
per_class_acc = []
for label in LABEL_NAMES:
    idxs    = [i for i, l in enumerate(true_6class) if l == label]
    correct = sum(1 for i in idxs if pred_6class[i] == label)
    per_class_acc.append(correct / len(idxs) if idxs else 0)

bars = ax.bar(LABEL_NAMES, per_class_acc,
              color=colors_dist, alpha=0.85,
              edgecolor="white", linewidth=0.5)
for bar, v in zip(bars, per_class_acc):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.01,
            f"{v:.2f}",
            ha="center", va="bottom", fontsize=8,
            fontweight="bold")
ax.axhline(y=acc_6, color="gray", linestyle="--",
           alpha=0.7, linewidth=1,
           label=f"Overall: {acc_6:.4f}")
ax.set_title("Per-Class Accuracy\n(LIAR Test Set, 6-Class)")
ax.set_xlabel("Label")
ax.set_ylabel("Accuracy")
ax.set_xticklabels(LABEL_NAMES, rotation=30, ha="right")
ax.set_ylim(0, 0.9)
ax.legend(fontsize=8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)

# L1c — Summary metrics bar
ax = axes[2]
metrics      = ["6-Class\nAccuracy", "6-Class\nMacro F1",
                "Binary\nAccuracy",  "Binary\nMacro F1"]
values       = [acc_6, mf1_6, acc_bin, mf1_bin]
metric_colors = ["#2196F3", "#4CAF50", "#9C27B0", "#FF5722"]

bars = ax.bar(metrics, values, color=metric_colors,
              alpha=0.85, edgecolor="white",
              linewidth=0.5, width=0.5)
for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.01,
            f"{v:.4f}",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold")
ax.set_title("DistilBERT Baseline Summary\n(LIAR Test Set)")
ax.set_ylabel("Score")
ax.set_ylim(0, 1.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.3, linewidth=0.5)

plt.suptitle("DistilBERT Baseline Evaluation on LIAR Dataset",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(pad=2.0)
path_l1 = os.path.join(OUTPUT_DIR, "liar_figure1_distribution_accuracy.png")
plt.savefig(path_l1, dpi=300, bbox_inches="tight",
            facecolor="white")
plt.close()
print(f"LIAR Figure 1 saved: {path_l1}")

# =========================================================
# FIGURE L2 — 6-Class Confusion Matrix
# =========================================================

cm_6 = confusion_matrix(true_6class, pred_6class,
                         labels=LABEL_NAMES)

fig, ax = plt.subplots(figsize=(8, 6.5))
sns.heatmap(cm_6, annot=True, fmt="d", cmap="Blues",
            xticklabels=LABEL_NAMES,
            yticklabels=LABEL_NAMES,
            ax=ax, cbar=True,
            linewidths=0.5, linecolor="white",
            annot_kws={"size": 9})
ax.set_xlabel("Predicted Label", fontsize=11)
ax.set_ylabel("True Label", fontsize=11)
ax.set_title(
    f"Confusion Matrix — DistilBERT on LIAR Test Set (6-Class)\n"
    f"Accuracy: {acc_6:.4f}  |  Macro F1: {mf1_6:.4f}",
    fontsize=11, fontweight="bold", pad=10
)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
plt.setp(ax.get_yticklabels(), rotation=0)
plt.tight_layout(pad=2.0)
path_l2 = os.path.join(OUTPUT_DIR, "liar_figure2_confusion_6class.png")
plt.savefig(path_l2, dpi=300, bbox_inches="tight",
            facecolor="white")
plt.close()
print(f"LIAR Figure 2 saved: {path_l2}")

# =========================================================
# FIGURE L3 — Binary Confusion Matrix
# =========================================================

cm_bin = confusion_matrix(true_binary, pred_binary,
                            labels=["false", "true"])

fig, ax = plt.subplots(figsize=(5, 4.5))
sns.heatmap(cm_bin, annot=True, fmt="d", cmap="Oranges",
            xticklabels=["False", "True"],
            yticklabels=["False", "True"],
            ax=ax, cbar=False,
            linewidths=1.0, linecolor="white",
            annot_kws={"size": 18, "weight": "bold"})
ax.set_xlabel("Predicted Label", fontsize=11)
ax.set_ylabel("True Label", fontsize=11)
ax.set_title(
    f"Confusion Matrix — Binary LIAR\n"
    f"Accuracy: {acc_bin:.4f}  |  Macro F1: {mf1_bin:.4f}",
    fontsize=11, fontweight="bold", pad=10
)
plt.tight_layout(pad=2.0)
path_l3 = os.path.join(OUTPUT_DIR, "liar_figure3_confusion_binary.png")
plt.savefig(path_l3, dpi=300, bbox_inches="tight",
            facecolor="white")
plt.close()
print(f"LIAR Figure 3 saved: {path_l3}")

# =========================================================
# FINAL SUMMARY — Print for paper
# =========================================================

print("\n" + "="*55)
print("FINAL NUMBERS FOR IEEE PAPER — LIAR DATASET")
print("="*55)
print(f"\nTable I: DistilBERT Baseline on LIAR")
print(f"  6-Class accuracy  : {acc_6:.4f}")
print(f"  6-Class Macro F1  : {mf1_6:.4f}")
print(f"  Binary accuracy   : {acc_bin:.4f}")
print(f"  Binary Macro F1   : {mf1_bin:.4f}")
print(f"  Test samples      : {len(test_data)}")
print(f"  Binary samples    : {len(binary_data)}")
print(f"\nAll figures saved to: {OUTPUT_DIR}")
print("\nDone.")