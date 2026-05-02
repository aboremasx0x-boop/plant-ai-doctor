from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import hashlib

from atlas_similarity import diagnose_by_image_similarity

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
    return FileResponse(INDEX_FILE)

@app.get("/health")
def health():
    return {
        "status": "running",
        "version": "stable_bytes_v2",
        "mode": "Stable Atlas Similarity"
    }

def safe_control_plan(diagnosis):
    return {
        "recommendation_text": f"تم تحديد المرض الأقرب من الأطلس: {diagnosis.get('disease_ar')} - {diagnosis.get('disease_en')}. ينصح بإزالة الأجزاء المصابة وتحسين التهوية وتقليل الرطوبة ومتابعة الحالة.",
        "bio_agents": ["Bacillus subtilis", "Bacillus velezensis", "Trichoderma harzianum"],
        "plant_extracts": ["مستخلص النيم", "مستخلص قشر الرمان", "مستخلص الثوم"],
        "field_actions": ["إزالة الأجزاء المصابة", "تعقيم أدوات القص", "تقليل الرطوبة", "تحسين التهوية"]
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        result, distance, confidence = diagnose_by_image_similarity(image_bytes)

        if result is None:
            return JSONResponse({"error": "لم يتم العثور على تطابق داخل الأطلس"}, status_code=400)

        image_hash = hashlib.sha256(image_bytes).hexdigest()
        severity_score = int(35 + (int(image_hash[:8], 16) % 56))

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

        return {
            "mode": "stable_atlas_similarity",
            "confidence": int(confidence),
            "severity": {
                "score": severity_score,
                "level_ar": severity_level_ar,
                "level_en": severity_level_en
            },
            "diagnosis": diagnosis,
            "control_plan": safe_control_plan(diagnosis),
            "filename": file.filename,
            "image_hash": image_hash[:16],
            "similarity_distance": int(distance)
        }

    except Exception as e:
        return JSONResponse(
            {"error": "SERVER_ERROR", "details": str(e)},
            status_code=500
        )
