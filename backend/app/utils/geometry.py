import math
from typing import Sequence


Point = Sequence[float]


def distance(p1: Point, p2: Point) -> float:
    return math.hypot(float(p1[0]) - float(p2[0]), float(p1[1]) - float(p2[1]))


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    return default if abs(b) < 1e-9 else a / b


def ratio(a: float, b: float) -> float:
    return safe_divide(a, b)


def normalize_distance(value: float, reference: float) -> float:
    return safe_divide(value, reference)


def angle_between_points(p1: Point, p2: Point) -> float:
    return math.degrees(math.atan2(float(p2[1]) - float(p1[1]), float(p2[0]) - float(p1[0])))


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def interval_score(value: float, good_min: float, good_max: float, ok_min: float, ok_max: float, max_score: float) -> float:
    if good_min <= value <= good_max:
        return max_score
    if ok_min <= value < good_min:
        span = max(good_min - ok_min, 1e-9)
        return max_score * (0.7 + 0.3 * (value - ok_min) / span)
    if good_max < value <= ok_max:
        span = max(ok_max - good_max, 1e-9)
        return max_score * (0.7 + 0.3 * (ok_max - value) / span)
    return max_score * 0.5
