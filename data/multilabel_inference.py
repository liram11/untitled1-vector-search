import pickle
import torch
import numpy as np
from categories import CATEGORIES

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

    # print(predictions)

    classes = mlb.inverse_transform(predictions.reshape(1, -1))

    if len(classes) > 0:
        classes = [CATEGORIES[x] for x in classes[0]]

    return classes, probs