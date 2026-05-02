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


def detect_physiological_disorders(image):
    """
    تمييز سريع بين:
    - عفن الطرف الزهري Blossom End Rot
    - لسعة الشمس Sun Scald
    """
    img = image.resize((300, 300)).convert("RGB")
    arr = np.array(img)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # طماطم حمراء
    red_pixels = (r > 120) & (g > 40) & (g < 150) & (b < 120)
    red_ratio = red_pixels.mean()

    # بقع سوداء داكنة: عفن الطرف الزهري
    dark_pixels = (r < 75) & (g < 70) & (b < 70)
    dark_ratio = dark_pixels.mean()

    # بقع فاتحة/بيضاء/مصفرّة: لسعة الشمس
    light_pixels = (r > 190) & (g > 160) & (b > 110)
    light_ratio = light_pixels.mean()

    # إذا الصورة ليست طماطم واضحة، لا نطبق هذه القاعدة
    if red_ratio < 0.06:
        return None

    # لسعة الشمس: وجود مساحة فاتحة محترقة
    if light_ratio > 0.012:
        return {
            "image": "physiological_detection",
            "page": 2,
            "hash": "sun_scald_rule",
            "disease_ar": "لسعة الشمس",
            "disease_en": "Sun Scald",
            "pathogen": "Environmental Stress",
            "pathogen_type_ar": "إجهاد بيئي",
            "pathogen_type_en": "Environmental Stress",
            "crop_ar": "الطماطم",
            "crop_en": "Tomato"
        }

    # عفن الطرف الزهري: بقعة داكنة واضحة
    if dark_ratio > 0.018:
        return {
            "image": "physiological_detection",
            "page": 1,
            "hash": "blossom_end_rot_rule",
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

    # أولًا: كشف الاضطرابات الفسيولوجية في الطماطم
    physio = detect_physiological_disorders(uploaded_image)
    if physio:
        return physio, 0, 94

    # ثانيًا: المقارنة مع صور الأطلس
    atlas_db = load_atlas_db()
    uploaded_hash = imagehash.phash(uploaded_image)

    best_match = None
    best_distance = 999

    for item in atlas_db:
        try:
            atlas_hash = imagehash.hex_to_hash(item["hash"])
            distance = int(uploaded_hash - atlas_hash)

            if distance < best_distance:
                best_distance = distance
                best_match = item

        except Exception:
            continue

    if best_match is None:
        raise ValueError("لم يتم العثور على تطابق داخل الأطلس")

    confidence = max(50, min(95, 100 - best_distance * 3))

    return best_match, int(best_distance), int(confidence)
