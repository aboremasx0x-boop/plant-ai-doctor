import json
import io
from pathlib import Path

from PIL import Image
import imagehash
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "atlas_db.json"


ATLAS_DISEASES_BY_CROP = {
    "Tomato": [
        "Blossom End Rot - عفن الطرف الزهري",
        "Sun Scald - لسعة الشمس",
        "Bacterial Wilt - الذبول البكتيري",
        "Bacterial Canker - التقرح البكتيري",
        "Bacterial Spot - التبقع البكتيري",
        "Pseudomonas Bacterial Speck - التبقع البكتيري بسيدوموناس",
        "Gray Mold - العفن الرمادي",
        "Anthracnose - الأنثراكنوز",
        "Septoria Leaf Spot - تبقع الأوراق السبتوري",
        "Early Blight - اللفحة المبكرة",
        "Late Blight - اللفحة المتأخرة",
        "Sclerotinia Rot - عفن الاسكليروتينيا",
        "Phytophthora Blight - لفحة الفيتوفثورا",
        "Brown Spot - التبقع البني",
        "Root Knot Nematode - تعقد الجذور النيماتودي",
        "TYLCV Yellow Leaf Curl - اصفرار والتفاف الأوراق",
        "ToMV Mosaic - الموزايك",
        "TSWV Spotted Wilt - الذبول المتبقع",
    ],
    "Potato": [
        "Potato Wart - ثآليل البطاطس",
        "Late Blight - اللفحة المتأخرة",
        "Early Blight - اللفحة المبكرة",
        "Rhizoctonia Canker/Wilt - عفن ولفحة وذبول الريزوكتونيا",
        "Black Rot - العفن الأسود",
        "Fusarium Wilt/Rot - عفن وذبول الفيوزاريوم",
        "Powdery Scab - الجرب المسحوقي",
        "Ring Rot - العفن الحلقي",
        "Brown Rot - الذبول الجنوبي البكتيري",
        "Soft Rot - العفن الطري البكتيري",
        "Ditylenchus Rot - العفن النيماتودي",
        "Pratylenchus Root Lesion - تقرح الجذر النيماتودي",
        "Potato Yellow Vein Virus - العرق الأصفر",
    ],
    "Onion": [
        "Botrytis Neck Rot - عفن البوتريتس",
        "Purple Blotch - اللفحة الأرجوانية",
        "Downy Mildew - البياض الزغبي",
        "Rust - الصدأ",
        "Stemphylium Blight - لفحة الاستمفيليوم",
        "Black Mold - العفن الأسود",
        "Smut - التفحم",
        "Xanthomonas Leaf Blight - لفحة الزانثوموناس",
        "Bacterial Soft Rot - العفن الطري البكتيري",
    ],
    "Cucurbits": [
        "Powdery Mildew - البياض الدقيقي",
        "Fruit Rot - عفن الثمار",
        "Phytophthora Blight - لفحة الفيتوفثورا",
        "Downy Mildew - البياض الزغبي",
        "Sclerotinia Rot - عفن الاسكليروتينيا",
        "Bacterial Wilt - الذبول الجنوبي البكتيري",
        "Bacterial Fruit Blotch - لفحة الثمار البكتيرية",
        "Squash Mosaic Virus - الموزايك الفيروسي",
    ],
    "Eggplant/Pepper": [
        "Blossom End Rot - عفن الطرف الزهري",
        "Phomopsis Fruit Rot - عفن الثمار الفوموبسيسي",
        "Phytophthora Blight - لفحة الفيتوفثورا",
        "Southern Blight - اللفحة الجنوبية",
    ],
    "Legumes": [
        "Sclerotinia Rot - عفن الاسكليروتينيا",
        "Septoria Leaf Spot - تبقع الأوراق السبتوري",
        "Powdery Mildew - البياض الدقيقي",
        "Gray Mold - العفن الرمادي",
        "Bean Anthracnose - أنثراكنوز الفول/الفاصوليا",
        "Rust - الصدأ",
        "Phoma Blight - لفحة الفوما",
        "Pythium Disease - مرض البيثيوم",
        "Charcoal Rot - العفن الفحمي",
        "White Leaf Spot - البقع البيضاء على الأوراق",
        "Bacterial Brown Spot - التبقع البني البكتيري",
        "Common Bacterial Blight - اللفحة العادية على الفاصوليا",
        "Stem and Bulb Nematode - نيماتودا السوق والأبصال",
        "Soybean Cyst Nematode - نيماتودا حويصلات فول الصويا",
    ],
    "Crucifers": [
        "Calcium Deficiency Symptoms - أعراض نقص الكالسيوم",
        "Downy Mildew - البياض الزغبي",
        "Black Spot - التبقع الأسود",
        "Clubroot - الجذر الصولجاني",
        "Sclerotinia Rot - عفن الاسكليروتينيا",
        "Phytophthora Stem and Root Rot - عفن الساق والجذر الفيتوفثوري",
        "Rhizoctonia Sudden Wilt - عفن وذبول الريزوكتونيا",
        "Soft Rot - العفن الطري البكتيري",
        "Black Rot - العفن الأسود البكتيري",
        "Bacterial Streak - التخطيط البكتيري",
        "Beet Cyst Nematode - نيماتودا حويصلات بنجر السكر",
        "Cabbage Leaf Curl Virus - فيروس التفاف أوراق الكرنب",
    ],
    "Cereals": [
        "Grain Smut - تفحم الحبوب",
        "Head Smut - تفحم الرأس",
        "Long Smut - التفحم الطويل",
        "Downy Mildew - البياض الزغبي",
        "Loose Smut of Wheat - التفحم السائب في القمح",
        "Covered Smut - التفحم المغطى",
        "Flag Smut - التفحم اللوائي",
        "Powdery Mildew of Wheat - البياض الدقيقي في القمح",
        "Seed Rot - عفن البذور",
        "Wheat Seed Gall Nematode - التثآلل النيماتودي",
        "Rice Blast - خناق الرقبة في الأرز",
        "Barley Leaf Spot - تبقع أوراق الشعير",
        "Loose Smut of Barley - التفحم السائب في الشعير",
    ],
    "Sugarcane/Maize/Cotton/Flax": [
        "Sugarcane Smut - تفحم السوط",
        "Sugarcane Gumming Disease - التصمغ البكتيري",
        "Ratoon Stunting Disease - تقزم الخلفة",
        "Sugarcane Mosaic Virus - موزايك القصب",
        "Pink Rot of Maize - العفن الوردي في الذرة الشامية",
        "Charcoal Rot of Maize - العفن الفحمي",
        "Late Wilt of Maize - الذبول المتأخر",
        "Common Smut of Maize - التفحم العادي",
        "Flax Rust - صدأ الكتان",
        "Dodder - حامول الكتان",
        "Cotton Seedling Damping-off - سقوط بادرات القطن",
        "Dry Boll Rot - عفن اللوز الجاف",
        "Ascochyta Blight - لفحة الأسكوكيتا",
        "Angular Leaf Spot of Cotton - التبقع الزاوي",
        "Fusarium Wilt of Cotton - الذبول الفيوزاريومي",
    ],
    "Fruit Trees": [
        "Fire Blight - اللفحة النارية",
        "Apple Powdery Mildew - البياض الدقيقي",
        "Apple Scab - جرب التفاح",
        "Phytophthora Canker - تقرح الجذوع الفيتوفثوري",
        "Penicillium Soft Rot - العفن الطري",
        "Apple Rust - صدأ التفاح",
        "Mango Powdery Mildew - البياض الدقيقي في المانجو",
        "Mango Anthracnose - أنثراكنوز المانجو",
        "Mango Malformation - التشوه في المانجو",
        "Stem-end Rot - عفن الطرف الخلفي/عفن الثمار",
        "Fig Rust - صدأ التين",
        "Powdery Mildew of Stone Fruits - البياض الدقيقي",
        "Shot Hole Disease - التثقيب",
        "Verticillium Wilt - الذبول الفرتسيليومي",
        "Peach Leaf Curl - تجعد أوراق الخوخ",
        "Bacterial Canker - التقرح البكتيري",
        "Bacterial Spot of Stone Fruits - التبقع البكتيري",
    ],
    "Citrus/Grape/Banana/Palm": [
        "Citrus Black Pit/Blight - اللفحة والنقرة السوداء",
        "Citrus Gummosis - تصمغ الموالح",
        "Citrus Canker - تقرح الموالح",
        "Citrus Tristeza Virus - التدهور السريع",
        "Citrus Slow Decline Nematode - التدهور البطيء",
        "Alternaria Fruit Rot of Citrus - عفن الثمار الألترناري",
        "Penicillium Fruit Rot - عفن الثمار",
        "Grape Downy Mildew - البياض الزغبي في العنب",
        "Grape Powdery Mildew - البياض الدقيقي في العنب",
        "Grape Anthracnose - أنثراكنوز العنب",
        "Grape Black Rot - العفن الأسود في العنب",
        "Banana Panama Disease - ذبول الموز الفيوزاريومي",
        "Banana Bunchy Top Virus - تورد القمة",
        "Banana Bacterial Wilt - الذبول البكتيري",
        "Cigar-end Rot - عفن طرف السيجار",
        "Bayoud Disease of Palm - البيوض",
        "Diplodia Rot of Palm - عفن الديبلوديا",
        "Black Scorch of Palm - اللفحة السوداء",
        "Graphiola Leaf Spot of Palm - الجرافيولا على الأوراق",
    ],
}


ATLAS_DISEASES = [
    disease.split(" - ")[0]
    for diseases in ATLAS_DISEASES_BY_CROP.values()
    for disease in diseases
]


def get_crop_by_disease(disease_en):
    for crop, diseases in ATLAS_DISEASES_BY_CROP.items():
        for disease in diseases:
            if disease_en == disease.split(" - ")[0]:
                return crop
    return "Unknown"


def load_atlas_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid = []
    for item in data:
        disease_en = item.get("disease_en", "Unknown")

        if not item.get("hash"):
            continue

        if disease_en == "Unknown":
            continue

        if disease_en not in ATLAS_DISEASES:
            continue

        crop_from_list = get_crop_by_disease(disease_en)
        if crop_from_list != "Unknown":
            item["crop_en"] = crop_from_list

        valid.append(item)

    if not valid:
        raise ValueError("atlas_db.json لا يحتوي على أمراض صالحة بعد الفلترة")

    return valid


def detect_physiological_disorders(image):
    img = image.resize((300, 300)).convert("RGB")
    arr = np.array(img)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    tomato_red = (r > 130) & (g > 35) & (g < 150) & (b < 120)
    green_plant = (g > 90) & (g > r * 1.15) & (g > b * 1.15)
    dark_spots = (r < 75) & (g < 70) & (b < 70)
    light_scars = (r > 190) & (g > 160) & (b > 110)

    red_ratio = tomato_red.mean()
    green_ratio = green_plant.mean()
    dark_ratio = dark_spots.mean()
    light_ratio = light_scars.mean()

    if green_ratio > 0.12 and red_ratio < 0.12:
        return None

    if red_ratio < 0.12:
        return None

    if light_ratio > 0.025 and dark_ratio < 0.05:
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

    physio = detect_physiological_disorders(uploaded_image)
    if physio:
        return physio, 0, 94

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
