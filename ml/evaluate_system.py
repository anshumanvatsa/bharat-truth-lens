import sys
import os

sys.path.append(os.path.abspath("../backend"))

import pandas as pd
from tqdm import tqdm

from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix
)

from app.services.analyzer import analyze_claim, predict_claim


# -----------------------------
# DATASET PATH
# -----------------------------

DATA_PATH = "data/liar/test.tsv"


# -----------------------------
# LOAD DATASET
# -----------------------------

data = pd.read_csv(
    DATA_PATH,
    sep="\t",
    header=None,
    engine="python",
    quoting=3
)

# LIAR dataset
# column 1 = label
# column 2 = statement

claims = data.iloc[:,2]
labels = data.iloc[:,1]


# -----------------------------
# LABEL CONVERSION
# -----------------------------

def convert_label(label):

    if label in ["false","pants-fire"]:
        return "false"

    elif label in ["barely-true","half-true"]:
        return "mixed"

    else:
        return "true"


truth = [convert_label(l) for l in labels]


# -----------------------------
# BASELINE
# -----------------------------

baseline_predictions = []

print("\nRunning DistilBERT baseline...\n")

for claim in tqdm(claims):

    prediction,_ = predict_claim(claim)

    if prediction not in ["true","false","mixed"]:
        prediction = "mixed"

    baseline_predictions.append(prediction)


# -----------------------------
# HYBRID SYSTEM
# -----------------------------

hybrid_predictions = []

print("\nRunning Hybrid system...\n")

for claim in tqdm(claims):

    result = analyze_claim(claim)

    pred = result["prediction"]

    if pred not in ["true","false","mixed"]:
        pred = "mixed"

    hybrid_predictions.append(pred)


# -----------------------------
# RESULTS
# -----------------------------

print("\n==============================")
print("BASELINE RESULTS")
print("==============================")

print("Accuracy:", accuracy_score(truth,baseline_predictions))

print(classification_report(truth,baseline_predictions))


print("\n==============================")
print("HYBRID SYSTEM RESULTS")
print("==============================")

print("Accuracy:", accuracy_score(truth,hybrid_predictions))

print(classification_report(truth,hybrid_predictions))


# -----------------------------
# CONFUSION MATRIX
# -----------------------------

print("\nConfusion Matrix (Hybrid)\n")

print(confusion_matrix(truth,hybrid_predictions))