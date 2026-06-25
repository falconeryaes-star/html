from dataclasses import dataclass
from typing import List

import cv2
import numpy as np

from app.services.face_detector import FaceDetectionResult
from app.utils.geometry import angle_between_points, clamp, distance


@dataclass
class QualityReport:
    blur: float
    brightness: float
    overexposed_ratio: float
    underexposed_ratio: float
    face_area_ratio: float
    yaw_proxy: float
    pitch_proxy: float
    roll_degrees: float
    score: int
    is_suitable: bool
    issues: List[str]


def _pt(face: FaceDetectionResult, idx: int) -> tuple[float, float]:
    x, y, _ = face.landmarks[idx]
    return x * face.image_width, y * face.image_height


def check_quality(image_bgr: np.ndarray, face: FaceDetectionResult | None) -> QualityReport:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    over = float((gray > 245).mean())
    under = float((gray < 18).mean())
    issues: List[str] = []

    if face is None:
        issues.append("未检测到清晰单人正脸")
        return QualityReport(blur, brightness, over, under, 0, 0, 0, 0, 0, False, issues)

    if face.face_count != 1:
        issues.append("检测到多张明显人脸，请上传单人照片")
        return QualityReport(blur, brightness, over, under, 0, 0, 0, 0, 0, False, issues)

    left, right, top, chin = _pt(face, 234), _pt(face, 454), _pt(face, 10), _pt(face, 152)
    nose, left_eye, right_eye, mouth = _pt(face, 1), _pt(face, 33), _pt(face, 263), _pt(face, 13)
    face_w = max(distance(left, right), 1.0)
    face_h = max(distance(top, chin), 1.0)
    face_area = (face_w * face_h) / max(face.image_width * face.image_height, 1)
    center_x = (left[0] + right[0]) / 2
    center_y = (top[1] + chin[1]) / 2
    yaw = abs(nose[0] - center_x) / face_w
    pitch = abs((nose[1] - center_y) / face_h)
    roll = abs(angle_between_points(left_eye, right_eye))

    if face_area < 0.08:
        issues.append("人脸区域偏小，五官比例不适合稳定分析")
    if yaw > 0.18:
        issues.append("头部左右偏转较明显，请尽量使用正脸照片")
    if pitch > 0.24:
        issues.append("头部俯仰角度较明显，请减少仰拍或低头")
    if roll > 12:
        issues.append("头部倾斜较明显，请保持头部端正")
    if blur < 45:
        issues.append("图片清晰度不足，关键点可能不稳定")
    if brightness < 45 or brightness > 215:
        issues.append("脸部光线过暗或过曝")
    if over > 0.18 or under > 0.22:
        issues.append("图片存在明显过曝或欠曝区域")

    score = int(clamp(100, 0, 100))
    score -= 24 if blur < 45 else 0
    score -= 18 if brightness < 45 or brightness > 215 else 0
    score -= 16 if face_area < 0.08 else 0
    score -= 14 if yaw > 0.18 else 0
    score -= 10 if pitch > 0.24 else 0
    score -= 8 if roll > 12 else 0
    score -= int(clamp((over + under) * 80, 0, 16))
    score = int(clamp(score, 0, 100))

    return QualityReport(
        blur=blur,
        brightness=brightness,
        overexposed_ratio=over,
        underexposed_ratio=under,
        face_area_ratio=face_area,
        yaw_proxy=yaw,
        pitch_proxy=pitch,
        roll_degrees=roll,
        score=score,
        is_suitable=not issues,
        issues=issues,
    )
