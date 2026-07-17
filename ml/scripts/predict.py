import torch
from transformers import DistilBertTokenizerFast
from transformers import DistilBertForSequenceClassification


tokenizer = DistilBertTokenizerFast.from_pretrained("ml/models/liar_model")
model = DistilBertForSequenceClassification.from_pretrained("ml/models/liar_model")


labels = [
    "pants-fire",
    "false",
    "barely-true",
    "half-true",
    "mostly-true",
    "true",
]


def predict(statement):
    inputs = tokenizer(statement, return_tensors="pt", truncation=True)

    outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)

    label_id = torch.argmax(probs).item()

    return labels[label_id]


print(predict("The unemployment rate is the lowest ever"))