from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from disease_reference import DISEASE_DATABASE
from recommendation_engine import smart_recommendation
import random

print("🔥 NEW API VERSION RUNNING")

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

app = FastAPI(title="Plant AI Doctor – Publish Version")

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
    return JSONResponse(
        {"error": "index.html not found", "path": str(INDEX_FILE)},
        status_code=500
    )

@app.get("/health")
def health():
    return {
        "status": "running",
        "system": "Plant AI Doctor",
        "mode": "AI Decision Engine"
    }

@app.get("/diseases")
def list_diseases():
    return DISEASE_DATABASE

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if "leaf" in filename or "ورقة" in filename:
        result = DISEASE_DATABASE[0]
    elif "spot" in filename or "بقع" in filename:
        result = DISEASE_DATABASE[4]
    elif "mold" in filename or "عفن" in filename:
        result = DISEASE_DATABASE[2]
    elif "wilt" in filename or "ذبول" in filename:
        result = DISEASE_DATABASE[3]
    else:
        result = random.choice(DISEASE_DATABASE)

    confidence = random.randint(88, 95)
    severity_score = random.randint(35, 90)

    if severity_score < 50:
        severity_level_ar = "منخفضة"
        severity_level_en = "Low"
    elif severity_score < 75:
        severity_level_ar = "متوسطة"
        severity_level_en = "Medium"
    else:
        severity_level_ar = "عالية"
        severity_level_en = "High"

    control_plan = smart_recommendation(result)

    return {
        "mode": "smart_ai_demo",
        "confidence": confidence,
        "severity": {
            "score": severity_score,
            "level_ar": severity_level_ar,
            "level_en": severity_level_en
        },
        "diagnosis": result,
        "control_plan": control_plan,
        "filename": file.filename
    }
