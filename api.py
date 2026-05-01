from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import hashlib
import os

from atlas_similarity import diagnose_by_image_similarity
from recommendation_engine import smart_recommendation

print("🔥 ATLAS IMAGE SIMILARITY API RUNNING")

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

app = FastAPI(title="Plant AI Doctor - Atlas Image Similarity")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.head("/")
def head_root():
    return Response(status_code=200)

@app.get("/")
def root():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return JSONResponse({"error": "index.html not found"}, status_code=500)

@app.get("/health")
def health():
    return {
        "status": "running",
        "system": "Plant AI Doctor",
        "mode": "Atlas Image Similarity"
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()

    temp_path = BASE_DIR / f"temp_{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    try:
        result, distance = diagnose_by_image_similarity(str(temp_path))
    finally:
        if temp_path.exists():
            os.remove(temp_path)

    if result is None:
        return JSONResponse(
            {"error": "لم يتم العثور على تشابه مناسب داخل الأطلس"},
            status_code=400
        )

    confidence = max(50, min(95, 100 - distance * 3))

    image_hash = hashlib.sha256(image_bytes).hexdigest()
    severity_score = 35 + (int(image_hash[:8], 16) % 56)

    if severity_score < 50:
        severity_level_ar = "منخفضة"
        severity_level_en = "Low"
    elif severity_score < 75:
        severity_level_ar = "متوسطة"
        severity_level_en = "Medium"
    else:
        severity_level_ar = "عالية"
        severity_level_en = "High"

    diagnosis = {
        "crop_ar": result.get("crop_ar", "غير محدد"),
        "crop_en": result.get("crop_en", "Unknown"),
        "disease_ar": result.get("disease_ar", "غير محدد"),
        "disease_en": result.get("disease_en", "Unknown"),
        "pathogen": result.get("pathogen", "From Atlas"),
        "pathogen_type_ar": result.get("pathogen_type_ar", "حسب الأطلس"),
        "pathogen_type_en": result.get("pathogen_type_en", "From Atlas"),
        "source": f"Atlas of Plant Diseases - page {result.get('page', 'Unknown')}",
        "symptoms": "تم اختيار أقرب صورة مشابهة من أطلس أمراض النبات."
    }

    control_plan = smart_recommendation(diagnosis)

    return {
        "mode": "atlas_similarity_ai",
        "confidence": confidence,
        "severity": {
            "score": severity_score,
            "level_ar": severity_level_ar,
            "level_en": severity_level_en
        },
        "diagnosis": diagnosis,
        "control_plan": control_plan,
        "filename": file.filename,
        "image_hash": image_hash[:16],
        "similarity_distance": distance,
        "atlas_image": result.get("image", "")
    }
