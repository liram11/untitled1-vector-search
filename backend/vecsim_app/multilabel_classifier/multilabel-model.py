# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3.9.12 64-bit
#     language: python
#     name: python3
# ---

# +
import json
import os
import re
import string

import numpy as np
import pandas as pd
import torch
from categories import CATEGORIES
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import (
    AutoTokenizer,
    BertForSequenceClassification,
    EvalPrediction,
    Trainer,
    TrainingArguments,
)

DATA_PATH = "arxiv-metadata-oai-snapshot.json"
YEAR_CUTOFF = 2012
YEAR_PATTERN = r"(19|20[0-9]{2})"
ML_CATEGORY = list(CATEGORIES.keys())


# +
def process(paper: dict):
    paper = json.loads(paper)
    if paper["journal-ref"]:
        years = [int(year) for year in re.findall(YEAR_PATTERN, paper["journal-ref"])]
        years = [year for year in years if (year <= 2022 and year >= 1991)]
        year = min(years) if years else None
    else:
        year = None
    return {
        "id": paper["id"],
        "title": paper["title"],
        "year": year,
        "authors": paper["authors"],
        "categories": ",".join(paper["categories"].split(" ")),
        "abstract": paper["abstract"],
    }


def papers():
    with open(DATA_PATH, "r") as f:
        for paper in f:
            paper = process(paper)
            if paper["year"]:
                if paper["year"] >= YEAR_CUTOFF:
                    yield paper


# -

df = pd.DataFrame(papers())
len(df)

df["text"] = df["title"] + " " + df["abstract"]
df["categories"] = df["categories"].apply(lambda x: x.split(","))

# +
# Split into train and test

from sklearn.model_selection import train_test_split

df_train, df_test = train_test_split(df, test_size=0.2)


# +
def get_tokenizer(tokenizer_model):
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_model)
    return tokenize_function, tokenizer


tokenize_function, tokenizer = get_tokenizer("bert-base-uncased")
# -

mlb = MultiLabelBinarizer()
mlb.fit(df_train["categories"])


def preprocess_data(examples):
    # take a batch of texts
    text = examples["text"]

    # encode them
    encoding = tokenizer(text, padding="max_length", truncation=True, max_length=128)

    encoded_categories = mlb.transform(examples["categories"]).astype(float)

    encoding["labels"] = encoded_categories

    return encoding


model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=len(mlb.classes_),
    problem_type="multi_label_classification",
)

# +
df_train_hf = Dataset.from_pandas(df_train[["text", "categories"]])
tokenized_train = df_train_hf.map(preprocess_data, batched=True)

df_test_hf = Dataset.from_pandas(df[["text", "categories"]])
tokenized_test = df_test_hf.map(preprocess_data, batched=True)

# +
# Debugging - get inverse transform

print(
    "Reversed",
    mlb.inverse_transform(np.asarray(tokenized_test[0]["labels"]).reshape(1, -1)),
)
print("Original categories", tokenized_test[0]["categories"])

# +
# Adaptation: https://github.com/NielsRogge/Transformers-Tutorials/blob/master/BERT/Fine_tuning_BERT_(and_friends)_for_multi_label_text_classification.ipynb
#
batch_size = 16
metric_name = "f1"

args = TrainingArguments(
    f"paper-multilabel-finetuning",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=15,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model=metric_name,
    # push_to_hub=True,
)


# source: https://jesusleal.io/2021/04/21/Longformer-multilabel-classification/
def multi_label_metrics(predictions, labels, threshold=0.5):
    # first, apply sigmoid on predictions which are of shape (batch_size, num_labels)
    sigmoid = torch.nn.Sigmoid()
    probs = sigmoid(torch.Tensor(predictions))
    # next, use threshold to turn them into integer predictions
    y_pred = np.zeros(probs.shape)
    y_pred[np.where(probs >= threshold)] = 1
    # finally, compute metrics
    y_true = labels
    f1_micro_average = f1_score(y_true=y_true, y_pred=y_pred, average="micro")
    roc_auc = roc_auc_score(y_true, y_pred, average="micro")
    accuracy = accuracy_score(y_true, y_pred)
    # return as dictionary
    metrics = {"f1": f1_micro_average, "roc_auc": roc_auc, "accuracy": accuracy}
    return metrics


def compute_metrics(p: EvalPrediction):
    preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
    result = multi_label_metrics(predictions=preds, labels=p.label_ids)
    return result


# -

trainer = Trainer(
    model,
    args,
    train_dataset=tokenized_test,
    eval_dataset=tokenized_test,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()

trainer.evaluate()

# +
text = df["text"].iloc[5]

encoding = tokenizer(text, return_tensors="pt")
encoding = {k: v.to(trainer.model.device) for k, v in encoding.items()}

outputs = trainer.model(**encoding)
logits = outputs.logits
# -

# apply sigmoid + threshold
sigmoid = torch.nn.Sigmoid()
probs = sigmoid(logits.squeeze().cpu())
predictions = np.zeros(probs.shape)
predictions[np.where(probs >= 0.5)] = 1

print(text)
print(mlb.inverse_transform(predictions.reshape(1, -1)))
