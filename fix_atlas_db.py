import json

# خريطة الأمراض حسب الصفحة (عدّلها لاحقًا إذا أردت)
PAGE_MAP = {
    1: ("Blossom End Rot", "عفن الطرف الزهري"),
    2: ("Sun Scald", "لسعة الشمس"),
    3: ("Bacterial Spot", "التبقع البكتيري"),
    4: ("Gray Mold", "العفن الرمادي"),
    5: ("Early Blight", "اللفحة المبكرة"),
    6: ("Late Blight", "اللفحة المتأخرة"),
    7: ("Anthracnose", "الأنثراكنوز"),
    8: ("Septoria Leaf Spot", "تبقع الأوراق السبتوري"),
}

with open("atlas_db.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    page = item["page"]

    if page in PAGE_MAP:
        disease_en, disease_ar = PAGE_MAP[page]
        item["disease_en"] = disease_en
        item["disease_ar"] = disease_ar

        item["pathogen"] = "From Atlas"
        item["crop_en"] = "Tomato"
        item["crop_ar"] = "الطماطم"

with open("atlas_db.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("تم إصلاح atlas_db.json بالكامل 🔥")