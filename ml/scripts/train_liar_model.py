import torch
from transformers import DistilBertTokenizerFast
from transformers import DistilBertForSequenceClassification
from transformers import Trainer, TrainingArguments
from datasets import Dataset

from dataset_loader import load_liar_dataset


train_df = load_liar_dataset("ml/data/liar/train.tsv")
valid_df = load_liar_dataset("ml/data/liar/valid.tsv")


tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")


def tokenize(example):
    return tokenizer(
        example["statement"],
        truncation=True,
        padding="max_length",
        max_length=128
    )


train_dataset = Dataset.from_pandas(train_df)
valid_dataset = Dataset.from_pandas(valid_df)

train_dataset = train_dataset.map(tokenize, batched=True)
valid_dataset = valid_dataset.map(tokenize, batched=True)


train_dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "label"],
)

valid_dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "label"],
)


model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=6
)


training_args = TrainingArguments(
    output_dir="ml/models/liar_model",
    eval_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=2,
    weight_decay=0.01,
    logging_steps=50,
    save_total_limit=1,
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
)


trainer.train()

trainer.save_model("ml/models/liar_model")

tokenizer.save_pretrained("ml/models/liar_model")