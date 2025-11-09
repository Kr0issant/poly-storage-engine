import torch
from transformers import pipeline
import json
from PIL import Image


def classify(img: Image):
    clip = pipeline(
    task="zero-shot-image-classification",
    model="openai/clip-vit-base-patch32",
    dtype=torch.bfloat16,
    device=0
    )
    with open("labels.json", "r") as labels:
        label_list = json.load(labels)
        predictions = clip(img, candidate_labels=label_list)
        return predictions

