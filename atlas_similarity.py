import io
import json
from pathlib import Path
from collections import Counter

import imagehash
import numpy as np
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "atlas_final_db.json"


def load_db():
    if not DB_FILE.exists():
        raise FileNotFoundError("atlas_final_db.json غير موجود")
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [
        x for x in data
        if x.get("disease_en") not in ["Unknown", "Skip", "", None]
        and x.get("hash")
    ]


def extract_features(image: Image.Image):
    img = image.resize((320, 320)).convert("RGB")
    arr = np.array(img).astype(np.float32)

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    red = (r > 120) & (g > 30) & (g < 175) & (b < 150)
    green = (g > 80) & (g > r * 1.03) & (g > b * 1.03)
    brown = (r > 65) & (r < 190) & (g > 35) & (g < 150) & (b < 135)
    dark = (r < 80) & (g < 75) & (b < 75)
    light = (r > 185) & (g > 155) & (b > 110)

    return {
        "red": float(red.mean()),
        "green": float(green.mean()),
        "brown": float(brown.mean()),
        "dark": float(dark.mean()),
        "light": float(light.mean()),
    }


def detect_plant_part(f):
    if f["green"] > 0.14 and f["brown"] > 0.012:
        return "stem"
    if f["green"] > 0.17:
        return "leaf"
    if f["red"] > 0.12 and f["green"] < 0.20:
        return "fruit"
    if f["brown"] > 0.13 and f["green"] < 0.12:
        return "root"
    return "unknown"


def compatible_part(db_part, detected_part):
    if detected_part == "unknown":
        return True
    if not db_part or db_part == "unknown":
        return True
    db_part = str(db_part).lower()
    detected_part = str(detected_part).lower()
    return db_part == detected_part or detected_part in db_part or db_part in detected_part


def blocked_diseases_by_part(detected_part):
    if detected_part in ["stem", "leaf", "root"]:
        return {"Blossom End Rot", "Sun Scald", "Fruit Rot", "Phomopsis Fruit Rot"}
    if detected_part == "fruit":
        return {
            "Root Knot Nematode",
            "Bacterial Wilt",
            "Fusarium Wilt/Rot",
            "Rhizoctonia Canker/Wilt",
            "Pratylenchus Root Lesion",
        }
    return set()


def disease_confidence(distance):
    return int(max(45, min(96, 100 - distance * 2.7)))


def diagnose_by_image_similarity(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    features = extract_features(image)
    detected_part = detect_plant_part(features)
    blocked = blocked_diseases_by_part(detected_part)

    db = load_db()
    if not db:
        raise ValueError("atlas_final_db.json لا يحتوي سجلات صالحة")

    ph = imagehash.phash(image)
    ah = imagehash.average_hash(image)
    dh = imagehash.dhash(image)

    scored = []

    for item in db:
        disease = item.get("disease_en", "")
        if disease in blocked:
            continue

        try:
            d1 = int(ph - imagehash.hex_to_hash(item["hash"]))
            d2 = int(ah - imagehash.hex_to_hash(item.get("ahash", item["hash"])))
            d3 = int(dh - imagehash.hex_to_hash(item.get("dhash", item["hash"])))
        except Exception:
            continue

        distance = (d1 * 0.55) + (d2 * 0.25) + (d3 * 0.20)

        db_part = item.get("plant_part", "unknown")
        if not compatible_part(db_part, detected_part):
            distance += 18

        scored.append((distance, item))

    if not scored:
        raise ValueError("لم يتم العثور على تطابق مناسب بعد الفلترة")

    scored.sort(key=lambda x: x[0])
    top5 = scored[:5]

    votes = Counter([item.get("disease_en", "Unknown") for _, item in top5])
    voted_disease = votes.most_common(1)[0][0]

    best_distance, best_item = top5[0]
    for dist, item in top5:
        if item.get("disease_en") == voted_disease:
            best_distance, best_item = dist, item
            break

    result = dict(best_item)
    result["detected_plant_part"] = detected_part
    result["image_features"] = features
    result["top_candidates"] = [
        {
            "disease_en": item.get("disease_en"),
            "disease_ar": item.get("disease_ar"),
            "crop_en": item.get("crop_en"),
            "plant_part": item.get("plant_part"),
            "distance": round(float(dist), 2),
        }
        for dist, item in top5
    ]

    return result, int(best_distance), disease_confidence(best_distance)