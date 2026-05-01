import fitz
import os
import io
import json
from PIL import Image
import imagehash

PDF_PATH = "atlas.pdf"
OUT_DIR = "atlas_images"
DB_FILE = "atlas_db.json"

os.makedirs(OUT_DIR, exist_ok=True)

# 🔥 ربط الصفحة بالمرض
PAGE_DISEASE_MAP = {
    3: ("Bacterial Spot", "التبقع البكتيري"),
    4: ("Gray Mold", "العفن الرمادي"),
    5: ("Early Blight", "اللفحة المبكرة"),
    6: ("Late Blight", "اللفحة المتأخرة"),
    7: ("Potato Diseases", "أمراض البطاطس"),
    12: ("Onion Diseases", "أمراض البصل"),
    15: ("Cucurbit Diseases", "أمراض القرعيات"),
    17: ("Legume Diseases", "أمراض البقوليات"),
    22: ("Crucifer Diseases", "أمراض الصليبيات"),
    25: ("Cereal Diseases", "أمراض الحبوب"),
    30: ("Fruit Diseases", "أمراض الفاكهة"),
    35: ("Citrus Diseases", "أمراض الموالح"),
    40: ("Palm Diseases", "أمراض النخيل")
}

doc = fitz.open(PDF_PATH)
records = []

for page_num in range(len(doc)):
    page = doc[page_num]
    images = page.get_images(full=True)

    for img_index, img in enumerate(images):
        xref = img[0]
        base = doc.extract_image(xref)
        image_bytes = base["image"]

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except:
            continue

        if image.width < 100 or image.height < 100:
            continue

        filename = f"page_{page_num+1}_img_{img_index+1}.jpg"
        path = os.path.join(OUT_DIR, filename)
        image.save(path)

        img_hash = str(imagehash.phash(image))

        # 🔥 تحديد المرض من الصفحة
        disease_en, disease_ar = PAGE_DISEASE_MAP.get(
            page_num + 1,
            ("Unknown", "غير محدد")
        )

        records.append({
            "image": path,
            "page": page_num + 1,
            "hash": img_hash,
            "disease_ar": disease_ar,
            "disease_en": disease_en,
            "pathogen": "From Atlas",
            "pathogen_type_ar": "حسب الأطلس",
            "pathogen_type_en": "From Atlas",
            "crop_ar": "حسب الصفحة",
            "crop_en": "From Atlas"
        })

with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print("تم بناء قاعدة الأطلس بالكامل بدون Unknown")