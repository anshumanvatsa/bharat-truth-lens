import pandas as pd


COLUMN_NAMES = [
    "label",
    "statement",
    "subject",
    "speaker",
    "speaker_job_title",
    "state_info",
    "party_affiliation",
    "barely_true_counts",
    "false_counts",
    "half_true_counts",
    "mostly_true_counts",
    "pants_on_fire_counts",
    "context",
]


def load_liar_dataset(path):
    df = pd.read_csv(path, sep="\t", header=None, names=COLUMN_NAMES)

    df = df[["statement", "label"]]

    label_map = {
        "pants-fire": 0,
        "false": 1,
        "barely-true": 2,
        "half-true": 3,
        "mostly-true": 4,
        "true": 5,
    }

    df["label"] = df["label"].map(label_map)

    return df