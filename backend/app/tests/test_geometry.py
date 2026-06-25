from app.utils.geometry import interval_score


def test_interval_score_keeps_small_deviation_high():
    score = interval_score(1.08, 0.95, 1.1, 0.75, 1.3, 10)
    assert score == 10


def test_interval_score_does_not_drop_to_zero_outside_range():
    score = interval_score(1.45, 0.95, 1.1, 0.75, 1.3, 10)
    assert score == 5
