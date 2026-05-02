import json
import io
from pathlib import Path
from PIL import Image
import imagehash

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "atlas_db.json"

def load_atlas_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        item for item in data
        if item.get("hash") and item.get("disease_en") != "Unknown"
    ]

def diagnose_by_image_similarity(image_bytes):
    atlas_db = load_atlas_db()

    uploaded_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
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
