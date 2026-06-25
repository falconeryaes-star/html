import numpy as np

from app.services.quality_checker import check_quality


def test_no_face_returns_not_suitable_without_score():
    image = np.zeros((128, 128, 3), dtype=np.uint8)
    result = check_quality(image, None)
    assert result.is_suitable is False
    assert result.score == 0
    assert result.issues
