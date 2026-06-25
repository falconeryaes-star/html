from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, CORS_ORIGINS
from app.schemas import AnalyzeNotSuitable, AnalyzeSuccess
from app.services.advice_generator import DISCLAIMER, generate_advantages, generate_suggestions, not_suitable_suggestions
from app.services.face_detector import FaceDetector
from app.services.landmark_analyzer import analyze_landmarks
from app.services.quality_checker import check_quality
from app.services.scoring import calculate_scores
from app.utils.image_io import read_image, save_upload_temp


app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

face_detector = FaceDetector()


@app.post("/analyze", response_model=AnalyzeSuccess | AnalyzeNotSuitable)
async def analyze(image: UploadFile = File(...)):
    temp_path: Path | None = None
    try:
        temp_path = await save_upload_temp(image)
        image_bgr = read_image(temp_path)
        face = face_detector.detect(image_bgr)
        quality = check_quality(image_bgr, face)

        if face is None or face.face_count != 1 or not quality.is_suitable:
            return AnalyzeNotSuitable(
                status="not_suitable",
                reason="当前照片不适合分析",
                issues=quality.issues or ["未检测到清晰单人正脸"],
                suggestions=not_suitable_suggestions(),
            )

        metrics = analyze_landmarks(face)
        score_data = calculate_scores(metrics, quality)
        return AnalyzeSuccess(
            status="success",
            overall_score=score_data["overall_score"],
            score_label=score_data["score_label"],
            photo_quality=score_data["photo_quality"],
            dimensions=score_data["dimensions"],
            advantages=generate_advantages(score_data),
            suggestions=generate_suggestions(score_data),
            disclaimer=DISCLAIMER,
        )
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
