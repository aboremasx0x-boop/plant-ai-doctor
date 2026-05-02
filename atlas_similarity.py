import json
import io
from pathlib import Path
from collections import Counter

from PIL import Image
import imagehash
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "atlas_db.json"


def load_atlas_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid = []
    for item in data:
        if item.get("hash") and item.get("disease_en") and item.get("disease_en") != "Unknown":
            valid.append(item)

    if not valid:
        raise ValueError("atlas_db.json لا يحتوي بيانات صالحة")

    return valid


def extract_features(image):
    img = image.resize((300, 300)).convert("RGB")
    arr = np.array(img)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    tomato_red = (r > 125) & (g > 35) & (g < 165) & (b < 135)
    green = (g > 85) & (g > r * 1.05) & (g > b * 1.05)
    dark = (r < 75) & (g < 70) & (b < 70)
    light = (r > 190) & (g > 160) & (b > 110)
    brown = (r > 75) & (r < 185) & (g > 35) & (g < 145) & (b < 120) & (r > g * 1.05)

    return {
        "red_ratio": float(tomato_red.mean()),
        "green_ratio": float(green.mean()),
        "dark_ratio": float(dark.mean()),
        "light_ratio": float(light.mean()),
        "brown_ratio": float(brown.mean()),
    }


def detect_plant_part(features):
    red = features["red_ratio"]
    green = features["green_ratio"]
    brown = features["brown_ratio"]

    if red > 0.12:
        return "fruit"

    if green > 0.18 and brown > 0.018:
        return "stem"

    if green > 0.16:
        return "leaf"

    if brown > 0.12 and green < 0.10:
        return "root"

    return "unknown"


def rule_based_tomato(features, plant_part):
    red = features["red_ratio"]
    green = features["green_ratio"]
    dark = features["dark_ratio"]
    light = features["light_ratio"]
    brown = features["brown_ratio"]

    # ثمرة طماطم: لسعة شمس
    if plant_part == "fruit" and red > 0.12 and light > 0.025 and dark < 0.05:
        return {
            "image": "rule_sun_scald",
            "page": 2,
            "plant_part": "fruit",
            "crop_ar": "الطماطم",
            "crop_en": "Tomato",
            "disease_ar": "لسعة الشمس",
            "disease_en": "Sun Scald",
            "pathogen": "Environmental Stress",
            "pathogen_type_ar": "إجهاد بيئي",
            "pathogen_type_en": "Environmental Stress",
        }, 0, 95

    # ثمرة طماطم: عفن الطرف الزهري
    if plant_part == "fruit" and red > 0.12 and dark > 0.018:
        return {
            "image": "rule_blossom_end_rot",
            "page": 1,
            "plant_part": "fruit",
            "crop_ar": "الطماطم",
            "crop_en": "Tomato",
            "disease_ar": "عفن الطرف الزهري",
            "disease_en": "Blossom End Rot",
            "pathogen": "Physiological Disorder",
            "pathogen_type_ar": "اضطراب فسيولوجي",
            "pathogen_type_en": "Physiological Disorder",
        }, 0, 95

    # ساق طماطم: تقرح بكتيري
    if plant_part == "stem" and green > 0.18 and brown > 0.025:
        return {
            "image": "rule_bacterial_canker",
            "page": 3,
            "plant_part": "stem",
            "crop_ar": "الطماطم",
            "crop_en": "Tomato",
            "disease_ar": "التقرح البكتيري",
            "disease_en": "Bacterial Canker",
            "pathogen": "Clavibacter michiganensis",
            "pathogen_type_ar": "بكتيريا",
            "pathogen_type_en": "Bacteria",
        }, 0, 93

    return None


def part_allowed(item_part, detected_part):
    if detected_part == "unknown":
        return True

    if not item_part or item_part == "unknown":
        return True

    if item_part == detected_part:
        return True

    if detected_part in item_part:
        return True

    if item_part in detected_part:
        return True

    if item_part == "stem_leaf_fruit" and detected_part in ["stem", "leaf", "fruit"]:
        return True

    if item_part == "fruit_leaf" and detected_part in ["fruit", "leaf"]:
        return True

    if item_part == "leaf_stem" and detected_part in ["leaf", "stem"]:
        return True

    return False


def filter_candidates(atlas_db, detected_part):
    filtered = [
        item for item in atlas_db
        if part_allowed(item.get("plant_part", "unknown"), detected_part)
    ]

    return filtered if filtered else atlas_db


def vote_top_results(scored, top_n=5):
    top = scored[:top_n]

    diseases = [item.get("disease_en", "Unknown") for _, item in top]
    vote = Counter(diseases).most_common(1)[0][0]

    for distance, item in top:
        if item.get("disease_en") == vote:
            return distance, item

    return scored[0]


def diagnose_by_image_similarity(image_bytes):
    uploaded_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    features = extract_features(uploaded_image)
    detected_part = detect_plant_part(features)

    # قواعد دقيقة قبل الأطلس
    rule = rule_based_tomato(features, detected_part)
    if rule:
        return rule

    atlas_db = load_atlas_db()
    candidates = filter_candidates(atlas_db, detected_part)

    uploaded_hash = imagehash.phash(uploaded_image)

    scored = []
    for item in candidates:
        try:
            atlas_hash = imagehash.hex_to_hash(item["hash"])
            distance = int(uploaded_hash - atlas_hash)

            # عقوبة إذا الجزء النباتي مختلف
            item_part = item.get("plant_part", "unknown")
            if not part_allowed(item_part, detected_part):
                distance += 12

            scored.append((distance, item))
        except Exception:
            continue

    if not scored:
        raise ValueError("لم يتم العثور على تطابق داخل الأطلس")

    scored.sort(key=lambda x: x[0])

    best_distance, best_match = vote_top_results(scored, top_n=5)

    best_match["detected_plant_part"] = detected_part
    best_match["image_features"] = features

    confidence = max(55, min(96, 100 - best_distance * 3))

    return best_match, int(best_distance), int(confidence)
