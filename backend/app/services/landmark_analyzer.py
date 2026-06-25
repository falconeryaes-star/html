from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING

from app.utils.geometry import distance, interval_score, safe_divide

if TYPE_CHECKING:
    from app.services.face_detector import FaceDetectionResult


@dataclass
class FaceMetrics:
    values: Dict[str, float]
    levels: Dict[str, str]


def _pt(face: FaceDetectionResult, idx: int) -> tuple[float, float]:
    x, y, _ = face.landmarks[idx]
    return x * face.image_width, y * face.image_height


def _avg(face: FaceDetectionResult, ids: list[int]) -> tuple[float, float]:
    xs, ys = zip(*[_pt(face, idx) for idx in ids])
    return sum(xs) / len(xs), sum(ys) / len(ys)


def analyze_landmarks(face: FaceDetectionResult) -> FaceMetrics:
    left, right, top, chin = _pt(face, 234), _pt(face, 454), _pt(face, 10), _pt(face, 152)
    face_width = max(distance(left, right), 1.0)
    face_height = max(distance(top, chin), 1.0)

    brow = _avg(face, [70, 63, 105, 336, 293, 300])
    nose_base = _avg(face, [2, 94, 19])
    upper = max(brow[1] - top[1], 1.0) * 1.18
    middle = max(nose_base[1] - brow[1], 1.0)
    lower = max(chin[1] - nose_base[1], 1.0)
    mean_third = (upper + middle + lower) / 3
    third_diff = max(abs(upper - mean_third), abs(middle - mean_third), abs(lower - mean_third)) / mean_third

    left_eye = distance(_pt(face, 33), _pt(face, 133))
    right_eye = distance(_pt(face, 362), _pt(face, 263))
    eye_width = max((left_eye + right_eye) / 2, 1.0)
    eye_gap = distance(_pt(face, 133), _pt(face, 362))

    cheek_width = distance(_pt(face, 234), _pt(face, 454))
    jaw_width = distance(_pt(face, 172), _pt(face, 397))
    lower_jaw_width = distance(_pt(face, 150), _pt(face, 379))
    forehead_width = distance(_pt(face, 103), _pt(face, 332))

    nose_width = distance(_pt(face, 49), _pt(face, 279))
    nose_length = distance(brow, nose_base)
    mouth_width = distance(_pt(face, 61), _pt(face, 291))
    lip_thickness = distance(_pt(face, 13), _pt(face, 14))
    mouth_center_offset = abs(_avg(face, [13, 14, 61, 291])[0] - (left[0] + right[0]) / 2) / face_width
    chin_offset = abs(chin[0] - (left[0] + right[0]) / 2) / face_width

    values = {
        "face_width": face_width,
        "face_height": face_height,
        "face_ratio": safe_divide(face_height, face_width),
        "upper_third": safe_divide(upper, face_height),
        "middle_third": safe_divide(middle, face_height),
        "lower_third": safe_divide(lower, face_height),
        "third_diff": third_diff,
        "five_eye_ratio": safe_divide(face_width, eye_width),
        "eye_gap_ratio": safe_divide(eye_gap, eye_width),
        "eye_width_diff": abs(left_eye - right_eye) / eye_width,
        "forehead_cheek_ratio": safe_divide(forehead_width, cheek_width),
        "cheek_jaw_ratio": safe_divide(jaw_width, cheek_width),
        "lower_jaw_ratio": safe_divide(lower_jaw_width, cheek_width),
        "chin_offset": chin_offset,
        "nose_face_ratio": safe_divide(nose_width, face_width),
        "nose_length_ratio": safe_divide(nose_length, face_height),
        "mouth_face_ratio": safe_divide(mouth_width, face_width),
        "lip_thickness_ratio": safe_divide(lip_thickness, mouth_width),
        "mouth_center_offset": mouth_center_offset,
    }

    levels = {
        "three_part_ratio": "较协调" if third_diff <= 0.15 else "可参考",
        "eye_spacing": "自然" if 0.85 <= values["eye_gap_ratio"] <= 1.15 else "较有辨识度",
        "contour": _contour_label(values),
    }
    return FaceMetrics(values=values, levels=levels)


def metric_score(value: float, good_min: float, good_max: float, ok_min: float, ok_max: float, max_score: float) -> float:
    return interval_score(value, good_min, good_max, ok_min, ok_max, max_score)


def _contour_label(values: Dict[str, float]) -> str:
    ratio = values["face_ratio"]
    jaw = values["cheek_jaw_ratio"]
    if ratio > 1.48:
        return "长脸倾向"
    if jaw > 0.86:
        return "方圆脸倾向"
    if jaw < 0.62:
        return "鹅蛋脸或心形脸倾向"
    return "鹅蛋脸与方圆脸之间"
