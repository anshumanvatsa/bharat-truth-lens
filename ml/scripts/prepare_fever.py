import json

def map_label(label):
    if label == "SUPPORTS":
        return "true"
    elif label == "REFUTES":
        return "false"
    else:
        return "uncertain"

input_path = "ml/data/fever_dev.jsonl"
output_path = "ml/data/fever_subset.json"

clean_data = []

print("Processing FEVER dataset...")

with open(input_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 150:  # limit dataset
            break
        item = json.loads(line)

        clean_data.append({
            "claim": item["claim"],
            "label": map_label(item["label"])
        })

with open(output_path, "w") as f:
    json.dump(clean_data, f, indent=2)

print(f"✅ Saved {len(clean_data)} samples to {output_path}")