import pickle
import torch
import numpy as np
from categories import CATEGORIES
from transformers import BertForSequenceClassification
from transformers import AutoTokenizer
import pickle

from typing import List

def predict_categories(text, model, tokenizer, mlb, proba_threshold = 0.5):

    encoding = tokenizer(text, return_tensors="pt")
    encoding = {k: v.to(model.device) for k, v in encoding.items()}

    outputs = model(**encoding)
    logits = outputs.logits

    # apply sigmoid + threshold
    sigmoid = torch.nn.Sigmoid()
    probs = sigmoid(logits.squeeze().cpu())
    predictions = np.zeros(probs.shape)
    predictions[np.where(probs >= proba_threshold)] = 1

    classes = mlb.inverse_transform(predictions.reshape(1, -1))

    if len(classes) > 0:
        classes = [CATEGORIES[x] for x in classes[0]]

    return classes, probs

def load_models(multilabel_model_path = 'categories', multilabel_binarizer_path = 'mlb.pkl'):
    model = BertForSequenceClassification.from_pretrained(
        multilabel_model_path,
        problem_type="multi_label_classification"
    )

    tokenizer = AutoTokenizer.from_pretrained(multilabel_model_path)

    with open(multilabel_binarizer_path, 'rb') as handle:
        mlb = pickle.load(handle)
    
    return model, tokenizer, mlb

def inference(queries: List[str], multilabel_model_path = 'categories', multilabel_binarizer_path = 'mlb.pkl'):

    model, tokenizer, mlb = load_models(multilabel_model_path, multilabel_binarizer_path)

    def flatten(l):
        return [item for sublist in l for item in sublist]
    
    categories = []

    for query in queries:
        cat, probs = predict_categories(query, model, tokenizer, mlb, proba_threshold = 0.15)

        categories.append(cat)

    categories = list(set(flatten(categories)))

    return {'predicted_categories': categories}

