import json
from PIL import Image
import imagehash

# تحميل قاعدة البيانات
with open("atlas_db.json", "r", encoding="utf-8") as f:
    atlas_db = json.load(f)

def get_image_hash(img_path):
    img = Image.open(img_path).convert("RGB")
    return imagehash.phash(img)

def diagnose_by_image_similarity(uploaded_image_path):
    query_hash = get_image_hash(uploaded_image_path)

    best_match = None
    best_distance = 999

    for item in atlas_db:
        atlas_hash = imagehash.hex_to_hash(item["hash"])
        distance = query_hash - atlas_hash

        if distance < best_distance:
            best_distance = distance
            best_match = item

    return best_match, best_distance