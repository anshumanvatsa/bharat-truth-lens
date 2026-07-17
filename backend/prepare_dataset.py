# prepare_dataset.py
# Creates balanced 500-sample FEVER dataset
# Place in D:\pulseindia-main\backend\
# Run: python prepare_dataset.py

import json
import random
import os

# Paths
SUBSET_PATH = os.path.join("..", "ml", "data", "fever_subset.json")
DEV_PATH    = os.path.join("..", "ml", "data", "fever_dev.jsonl")
OUTPUT_PATH = os.path.join("..", "ml", "data", "fever_eval_500.json")  # CHANGED: 300 → 500

# ── STEP 1: Load subset (your existing 112 binary samples) ──
with open(SUBSET_PATH) as f:
    subset = json.load(f)

subset_binary = [d for d in subset if d["label"] in ["true", "false"]]
subset_claims = {d["claim"] for d in subset_binary}  # track to avoid duplicates

print(f"Existing subset binary samples : {len(subset_binary)}")

# ── STEP 2: Load dev.jsonl ───────────────────────────────────
dev_data = []

with open(DEV_PATH, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())

        # Map FEVER labels → binary
        if item["label"] == "SUPPORTS":
            label = "true"
        elif item["label"] == "REFUTES":
            label = "false"
        else:
            continue  # skip NOT ENOUGH INFO

        claim = item["claim"].strip()

        # Skip if already in existing subset (avoid duplicates)
        if claim in subset_claims:
            continue

        # Skip very short claims (likely noisy)
        if len(claim.split()) < 5:
            continue

        dev_data.append({
            "claim": claim,
            "label": label
        })

print(f"Dev usable samples (new only)  : {len(dev_data)}")

# ── STEP 3: Combine both sources ─────────────────────────────
all_data = subset_binary + dev_data

true_samples  = [d for d in all_data if d["label"] == "true"]
false_samples = [d for d in all_data if d["label"] == "false"]

print(f"Total TRUE  available : {len(true_samples)}")
print(f"Total FALSE available : {len(false_samples)}")

# ── STEP 4: Sample balanced 250 true + 250 false ─────────────
# CHANGED: 150/150 → 250/250 for 500 total
random.seed(42)  # reproducible

n = min(250, len(true_samples), len(false_samples))

selected = random.sample(true_samples, n) + random.sample(false_samples, n)
random.shuffle(selected)

# ── STEP 5: Save ──────────────────────────────────────────────
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(selected, f, indent=2, ensure_ascii=False)

print("\n✅ DATASET CREATED")
print(f"Saved {len(selected)} samples to fever_eval_500.json")
print(f"True  : {sum(1 for d in selected if d['label'] == 'true')}")
print(f"False : {sum(1 for d in selected if d['label'] == 'false')}")
print("\nNext step: update DATA_PATH in ablation_study.py to fever_eval_500.json")