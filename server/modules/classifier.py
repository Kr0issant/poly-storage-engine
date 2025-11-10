from torch import bfloat16
from transformers import pipeline
import json
from PIL import Image
import os

clip_pipeline = None

def get_clip_pipeline():
    global clip_pipeline

    if clip_pipeline is None:
        clip_pipeline = pipeline(
            task = "zero-shot-image-classification",
            model = "openai/clip-vit-base-patch32",
            dtype = bfloat16,
            device = 0
        )
    return clip_pipeline

def classify(img: Image):
    with open("modules/labels.json", "r") as labels:
        clip = get_clip_pipeline()
        label_list = json.load(labels)
        predictions = clip(Image.fromarray(img, 'RGB'), candidate_labels=label_list)
    return predictions[:3]