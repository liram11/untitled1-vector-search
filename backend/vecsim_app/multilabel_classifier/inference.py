import pickle
from typing import List

import numpy as np
import torch
from ..categories import CATEGORIES
from transformers import AutoTokenizer, BertForSequenceClassification


def predict_categories_on_single_text(text, model, tokenizer, mlb, proba_threshold=0.5):

    encoding = tokenizer(text, return_tensors="pt")
    encoding = {k: v.to(model.device) for k, v in encoding.items()}

    print('encoding', encoding)
    outputs = model(**encoding)
    print('outputs', outputs)
    logits = outputs.logits

    # apply sigmoid + threshold
    sigmoid = torch.nn.Sigmoid()
    probs = sigmoid(logits.squeeze().cpu())
    predictions = np.zeros(probs.shape)
    predictions[np.where(probs >= proba_threshold)] = 1
    print(predictions)

    classes = mlb.inverse_transform(predictions.reshape(1, -1))

    if len(classes) > 0:
        classes = [CATEGORIES[x] for x in classes[0]]

    return classes, probs


def load_models(
    multilabel_model_path="categories", multilabel_binarizer_path="mlb.pkl"
):
    model = BertForSequenceClassification.from_pretrained(
        multilabel_model_path, problem_type="multi_label_classification"
    )

    tokenizer = AutoTokenizer.from_pretrained(multilabel_model_path)

    with open(multilabel_binarizer_path, "rb") as handle:
        mlb = pickle.load(handle)

    return model, tokenizer, mlb


def predict_categories(
    queries: List[str],
    model, tokenizer, mlb,proba_threshold=0.15
):

    def flatten(l):
        return [item for sublist in l for item in sublist]

    categories = []

    for query in queries:
        cat, probs = predict_categories_on_single_text(
            query, model, tokenizer, mlb, proba_threshold=proba_threshold
        )

        categories.append(cat)

    categories = list(set(flatten(categories)))

    return categories
