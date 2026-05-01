import json
import io
from pathlib import Path
from PIL import Image
import imagehash

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "atlas_db.json"

def load_atlas_db():
    if not DB_FILE.exists():
        raise FileNotFoundError("atlas_db.json غير موجود")

    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid = []
    for item in data:
        if item.get("hash") and item.get("disease_en") != "Unknown":
            valid.append(item)

    if not valid:
        raise ValueError("atlas_db.json لا يحتوي أمراض مصنفة")

    return valid

def diagnose_by_image_similarity(image_bytes):
    atlas_db = load_atlas_db()

    uploaded_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    uploaded_hash = imagehash.phash(uploaded_image)

    best_match = None
    best_distance = 999

    for item in atlas_db:
        try:
            atlas_hash = imagehash.hex_to_hash(item["hash"])
            distance = uploaded_hash - atlas_hash

            if distance < best_distance:
                best_distance = distance
                best_match = item
        except Exception:
            continue

    if best_match is None:
        raise ValueError("لم يتم العثور على تطابق داخل الأطلس")

    confidence = max(50, min(95, 100 - best_distance * 3))

    return best_match, best_distance, confidence
