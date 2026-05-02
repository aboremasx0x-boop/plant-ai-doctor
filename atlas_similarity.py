import json
import io
from pathlib import Path
from PIL import Image
import imagehash
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "atlas_db.json"

def load_atlas_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        item for item in data
        if item.get("hash") and item.get("disease_en") != "Unknown"
    ]

def detect_blossom_end_rot(image):
    img = image.resize((300, 300)).convert("RGB")
    arr = np.array(img)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    red_pixels = (r > 120) & (g > 40) & (g < 140) & (b < 100)
    dark_pixels = (r < 80) & (g < 70) & (b < 60)

    red_ratio = red_pixels.mean()
    dark_ratio = dark_pixels.mean()

    if red_ratio > 0.08 and dark_ratio > 0.015:
        return {
            "image": "physiological_detection",
            "page": 1,
            "hash": "physiological",
            "disease_ar": "عفن الطرف الزهري",
            "disease_en": "Blossom End Rot",
            "pathogen": "Physiological Disorder",
            "pathogen_type_ar": "اضطراب فسيولوجي",
            "pathogen_type_en": "Physiological Disorder",
            "crop_ar": "الطماطم",
            "crop_en": "Tomato"
        }

    return None

def diagnose_by_image_similarity(image_bytes):
    uploaded_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    physio = detect_blossom_end_rot(uploaded_image)
    if physio:
        return physio, 0, 94

    atlas_db = load_atlas_db()
    uploaded_hash = imagehash.phash(uploaded_image)

    best_match = None
    best_distance = 999

    for item in atlas_db:
        atlas_hash = imagehash.hex_to_hash(item["hash"])
        distance = int(uploaded_hash - atlas_hash)

        if distance < best_distance:
            best_distance = distance
            best_match = item

    confidence = max(50, min(95, 100 - best_distance * 3))

    return best_match, int(best_distance), int(confidence)
