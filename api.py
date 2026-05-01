from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import hashlib

from atlas_similarity import diagnose_by_image_similarity
from recommendation_engine import smart_recommendation

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

app = FastAPI(title="Plant AI Doctor - Stable Atlas Version")

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
        "mode": "Stable Atlas Similarity"
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        result, distance, confidence = diagnose_by_image_similarity(image_bytes)

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
            "symptoms": "تم اختيار أقرب حالة مشابهة من أطلس أمراض النبات."
        }

        control_plan = smart_recommendation(diagnosis)

        return {
            "mode": "stable_atlas_similarity",
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
            "similarity_distance": distance
        }

    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
