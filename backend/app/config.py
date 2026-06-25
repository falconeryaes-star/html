from pathlib import Path


APP_NAME = "Face Proportion and Image Advice Analyzer"
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
TMP_DIR = Path(__file__).resolve().parents[1] / "tmp"

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
