from __future__ import annotations

from typing import Dict, TYPE_CHECKING

from app.services.landmark_analyzer import FaceMetrics, metric_score
from app.utils.geometry import clamp, interval_score

if TYPE_CHECKING:
    from app.services.quality_checker import QualityReport


def level(score: int, max_score: int) -> str:
    ratio = score / max(max_score, 1)
    if ratio >= 0.9:
        return "优秀"
    if ratio >= 0.78:
        return "较协调"
    if ratio >= 0.65:
        return "正常"
    return "仅作参考"


def score_label(score: int) -> str:
    if score >= 95:
        return "高度出众型"
    if score >= 90:
        return "非常协调型"
    if score >= 85:
        return "优势明显型"
    if score >= 80:
        return "协调耐看型"
    if score >= 75:
        return "整体较好型"
    if score >= 70:
        return "自然清爽型"
    if score >= 60:
        return "基础正常型"
    return "建议更换照片后重新分析"


def calculate_scores(metrics: FaceMetrics, quality: QualityReport) -> Dict:
    v = metrics.values

    three_part = interval_score(v["third_diff"], 0.0, 0.08, 0.0, 0.3, 10)
    five_eye = interval_score(v["eye_gap_ratio"], 0.85, 1.15, 0.7, 1.35, 8)
    whitespace = interval_score(v["face_ratio"], 1.15, 1.55, 0.95, 1.85, 7)
    face_proportion_25 = round(three_part + five_eye + whitespace)

    contour_flow = (
        metric_score(v["face_ratio"], 1.12, 1.55, 0.95, 1.88, 8) * 0.34
        + metric_score(v["cheek_jaw_ratio"], 0.55, 0.9, 0.42, 1.05, 8) * 0.28
        + metric_score(v["forehead_cheek_ratio"], 0.62, 0.98, 0.45, 1.15, 8) * 0.18
        + metric_score(v["chin_offset"], 0.0, 0.07, 0.0, 0.16, 8) * 0.2
    )
    jaw_chin = (
        metric_score(v["lower_jaw_ratio"], 0.34, 0.72, 0.22, 0.88, 6) * 0.55
        + metric_score(v["chin_offset"], 0.0, 0.08, 0.0, 0.18, 6) * 0.45
    )
    dimensionality = interval_score(quality.brightness, 65, 180, 35, 220, 6)
    contour_20 = round(contour_flow + jaw_chin + dimensionality)

    eye_score = (
        metric_score(v["eye_width_diff"], 0.0, 0.12, 0.0, 0.28, 8) * 0.45
        + metric_score(v["eye_gap_ratio"], 0.85, 1.15, 0.7, 1.35, 8) * 0.35
        + 8 * 0.2
    )
    nose_score = (
        metric_score(v["nose_face_ratio"], 0.18, 0.33, 0.12, 0.42, 7) * 0.55
        + metric_score(v["nose_length_ratio"], 0.24, 0.42, 0.16, 0.52, 7) * 0.45
    )
    lip_score = (
        metric_score(v["mouth_face_ratio"], 0.28, 0.48, 0.18, 0.62, 5) * 0.62
        + metric_score(v["lip_thickness_ratio"], 0.08, 0.28, 0.03, 0.42, 5) * 0.38
    )
    harmony = interval_score(v["mouth_center_offset"], 0.0, 0.08, 0.0, 0.2, 5)
    feature_25 = round(eye_score + nose_score + lip_score + harmony)

    skin_15 = round(
        interval_score(quality.brightness, 65, 180, 35, 220, 6)
        + interval_score(quality.overexposed_ratio + quality.underexposed_ratio, 0, 0.08, 0, 0.35, 5)
        + interval_score(quality.blur, 80, 99999, 35, 80, 4)
    )

    photogenic_15 = round(
        interval_score(quality.yaw_proxy, 0, 0.12, 0, 0.18, 5)
        + interval_score(quality.roll_degrees, 0, 8, 0, 12, 5)
        + interval_score(quality.score, 80, 100, 45, 80, 5)
    )

    a = round(face_proportion_25 / 25 * 12)
    b = round(contour_20 / 20 * 10)
    c = round(feature_25 / 25 * 10)
    d = round(skin_15 / 15 * 5)
    e = round(photogenic_15 / 15 * 5)
    penalty = round(clamp((100 - quality.score) / 100 * 12, 0, 12))
    overall = int(clamp(60 + a + b + c + d + e - penalty, 45, 98))

    return {
        "overall_score": overall,
        "score_label": score_label(overall),
        "photo_quality": {
            "score": quality.score,
            "is_suitable": quality.is_suitable,
            "issues": quality.issues,
        },
        "dimensions": {
            "face_proportion": {
                "score": face_proportion_25,
                "max_score": 25,
                "level": level(face_proportion_25, 25),
                "details": {
                    "three_part_ratio": {
                        "upper": round(v["upper_third"], 3),
                        "middle": round(v["middle_third"], 3),
                        "lower": round(v["lower_third"], 3),
                        "comment": metrics.levels["three_part_ratio"],
                    },
                    "five_eye_ratio": {
                        "eye_spacing_level": metrics.levels["eye_spacing"],
                        "eye_gap_ratio": round(v["eye_gap_ratio"], 3),
                        "comment": "眼距与脸宽关系按区间评分，仅作照片参考",
                    },
                },
            },
            "face_contour": {
                "score": contour_20,
                "max_score": 20,
                "level": level(contour_20, 20),
                "details": {
                    "face_shape_tendency": metrics.levels["contour"],
                    "face_ratio": round(v["face_ratio"], 3),
                    "cheek_jaw_ratio": round(v["cheek_jaw_ratio"], 3),
                },
            },
            "feature_harmony": {
                "score": feature_25,
                "max_score": 25,
                "level": level(feature_25, 25),
                "details": {
                    "nose_face_ratio": round(v["nose_face_ratio"], 3),
                    "mouth_face_ratio": round(v["mouth_face_ratio"], 3),
                    "eye_width_diff": round(v["eye_width_diff"], 3),
                },
            },
            "skin_and_state": {
                "score": skin_15,
                "max_score": 15,
                "level": level(skin_15, 15),
                "details": {"brightness": round(quality.brightness, 1), "blur": round(quality.blur, 1)},
            },
            "photogenic_expression": {
                "score": photogenic_15,
                "max_score": 15,
                "level": level(photogenic_15, 15),
                "details": {
                    "yaw_proxy": round(quality.yaw_proxy, 3),
                    "roll_degrees": round(quality.roll_degrees, 2),
                },
            },
        },
        "internal_formula": {
            "base": 60,
            "A": a,
            "B": b,
            "C": c,
            "D": d,
            "E": e,
            "P": penalty,
        },
    }
