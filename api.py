from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import hashlib

from atlas_similarity import diagnose_by_image_similarity

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

app = FastAPI(title="Plant AI Doctor - V3 Atlas System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def severity_level(confidence):
    if confidence >= 85:
        return "High", "عالية", 79
    if confidence >= 65:
        return "Medium", "متوسطة", 60
    return "Low", "منخفضة", 35


def safe_recommendation(disease_en, pathogen_type_en):
    if pathogen_type_en == "Bacteria":
        return "يوصى بإزالة الأجزاء شديدة الإصابة، تعقيم أدوات القص، تقليل الرطوبة، وتحسين التهوية. يمكن استخدام عوامل حيوية مساعدة مثل Bacillus subtilis أو Bacillus velezensis حسب الحالة."
    if pathogen_type_en == "Fungus":
        return "يوصى بإزالة الأجزاء المصابة، تقليل الرطوبة، تحسين التهوية، واستخدام مكافحة حيوية مثل Trichoderma harzianum أو Bacillus spp. حسب المحصول."
    if pathogen_type_en == "Oomycete":
        return "يوصى بتحسين الصرف، تقليل الرطوبة حول النبات، إزالة الأنسجة المصابة، والمتابعة الحقلية الدقيقة."
    if pathogen_type_en == "Virus":
        return "يوصى بإزالة النباتات شديدة الإصابة، مكافحة الحشرات الناقلة، وتجنب نقل العدوى ميكانيكيًا."
    if pathogen_type_en == "Nematode":
        return "يوصى بتحليل التربة، استخدام دورة زراعية، وتحسين صحة الجذور والتربة."
    return "تشخيص مبدئي. يوصى بمراجعة الأعراض حقليًا أو تأكيدها مختبريًا عند الحاجة."


@app.get("/")
def root():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return {"status": "Plant AI Doctor V3 is running"}


@app.get("/health")
def health():
    return {"status": "ok", "version": "V3 Atlas Hybrid"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image_id = hashlib.md5(image_bytes).hexdigest()

        result, distance, confidence = diagnose_by_image_similarity(image_bytes)

        disease_en = result.get("disease_en", "Unknown")
        disease_ar = result.get("disease_ar", "غير معروف")
        crop_en = result.get("crop_en", "Unknown")
        crop_ar = result.get("crop_ar", "غير معروف")
        pathogen = result.get("pathogen", "From Atlas")
        pathogen_type_en = result.get("pathogen_type_en", "Unknown")
        pathogen_type_ar = result.get("pathogen_type_ar", "غير معروف")

        sev_en, sev_ar, severity_percent = severity_level(confidence)

        return JSONResponse({
            "success": True,
            "system": "AI Decision Engine V3",
            "image_id": image_id,
            "confidence": confidence,
            "distance": distance,
            "severity": {
                "level_en": sev_en,
                "level_ar": sev_ar,
                "percent": severity_percent,
            },
            "crop_en": crop_en,
            "crop_ar": crop_ar,
            "disease_en": disease_en,
            "disease_ar": disease_ar,
            "pathogen": pathogen,
            "pathogen_type_en": pathogen_type_en,
            "pathogen_type_ar": pathogen_type_ar,
            "plant_part": result.get("detected_plant_part", result.get("plant_part", "unknown")),
            "source": f"Atlas of Plant Diseases - page {result.get('page', 'unknown')}",
            "symptoms": "تم اختيار أقرب حالة مشابهة من أطلس أمراض النبات بعد فلترة المحصول والجزء النباتي.",
            "recommendation": safe_recommendation(disease_en, pathogen_type_en),
            "top_candidates": result.get("top_candidates", []),
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "حدث خطأ أثناء التشخيص. تأكد من وجود atlas_final_db.json وأنه يحتوي سجلات صالحة."
            }
        )