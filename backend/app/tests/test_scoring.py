from app.services.landmark_analyzer import FaceMetrics
from app.services.quality_checker import QualityReport
from app.services.scoring import calculate_scores


def sample_metrics():
    return FaceMetrics(
        values={
            "face_ratio": 1.35,
            "upper_third": 0.33,
            "middle_third": 0.34,
            "lower_third": 0.33,
            "third_diff": 0.04,
            "five_eye_ratio": 5.0,
            "eye_gap_ratio": 1.0,
            "eye_width_diff": 0.06,
            "forehead_cheek_ratio": 0.78,
            "cheek_jaw_ratio": 0.72,
            "lower_jaw_ratio": 0.52,
            "chin_offset": 0.03,
            "nose_face_ratio": 0.24,
            "nose_length_ratio": 0.34,
            "mouth_face_ratio": 0.38,
            "lip_thickness_ratio": 0.18,
            "mouth_center_offset": 0.02,
        },
        levels={"three_part_ratio": "较协调", "eye_spacing": "自然", "contour": "鹅蛋脸与方圆脸之间"},
    )


def sample_quality():
    return QualityReport(
        blur=120,
        brightness=125,
        overexposed_ratio=0.02,
        underexposed_ratio=0.01,
        face_area_ratio=0.16,
        yaw_proxy=0.04,
        pitch_proxy=0.05,
        roll_degrees=2,
        score=92,
        is_suitable=True,
        issues=[],
    )


def test_final_score_is_bounded_and_normal_input_not_too_low():
    result = calculate_scores(sample_metrics(), sample_quality())
    assert 45 <= result["overall_score"] <= 98
    assert result["overall_score"] >= 70


def test_internal_formula_exists():
    result = calculate_scores(sample_metrics(), sample_quality())
    assert result["internal_formula"]["base"] == 60
    assert 0 <= result["internal_formula"]["P"] <= 12
