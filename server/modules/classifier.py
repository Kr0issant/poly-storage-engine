from torch import bfloat16
from transformers import pipeline, CLIPModel, CLIPProcessor
from pathlib import Path
import json
from PIL import Image
import os

clip_pipeline = None

LOCAL_MODEL_DIR = Path("./local_clip_cache").resolve()
MODEL_NAME = "openai/clip-vit-base-patch32"

def classify(img: Image):
    with open("modules/classification.json", "r") as data:
        clip = get_clip_pipeline()

        if clip is None:
            return []

        label_list = json.load(data).keys()
        predictions = clip(Image.fromarray(img, 'RGB'), candidate_labels=label_list)
    return predictions[:3]

def get_clip_pipeline():
    global clip_pipeline

    if clip_pipeline is None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        
        download_model_if_not_exists()
        
        try:
            print(f"Loading model components from: {LOCAL_MODEL_DIR}")

            clip_pipeline = pipeline(
                task = "zero-shot-image-classification",
                model = str(LOCAL_MODEL_DIR),
                dtype = bfloat16,
                device = 0,
                local_files_only=True
            )
        except Exception as e:
            print(f"Error loading model offline: {e}")
            print(f"Please ensure the model '{MODEL_NAME}' is cached locally.")
            clip_pipeline = None

    return clip_pipeline

def download_model_if_not_exists():
    if not os.path.exists(LOCAL_MODEL_DIR) or not os.listdir(LOCAL_MODEL_DIR):
        print(f"Model not found locally in '{LOCAL_MODEL_DIR}'. Attempting to download...")
        try:
            os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
            
            model = CLIPModel.from_pretrained(MODEL_NAME)
            processor = CLIPProcessor.from_pretrained(MODEL_NAME)
            
            model.save_pretrained(LOCAL_MODEL_DIR)
            processor.save_pretrained(LOCAL_MODEL_DIR)
            print(f"Model successfully downloaded and saved to '{LOCAL_MODEL_DIR}'.")
            
        except Exception as e:
            print(f"Failed to download model. Check internet connection and permissions. Error: {e}")
            raise RuntimeError("Model download failed. Cannot proceed without the model files.")

        