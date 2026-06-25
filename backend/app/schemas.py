from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel


class PhotoQuality(BaseModel):
    score: int
    is_suitable: bool
    issues: List[str]


class Dimension(BaseModel):
    score: int
    max_score: int
    level: str
    details: Dict[str, Any] = {}


class AnalyzeSuccess(BaseModel):
    status: Literal["success"]
    overall_score: int
    score_label: str
    photo_quality: PhotoQuality
    dimensions: Dict[str, Dimension]
    advantages: List[str]
    suggestions: List[str]
    disclaimer: str


class AnalyzeNotSuitable(BaseModel):
    status: Literal["not_suitable"]
    reason: str
    issues: List[str]
    suggestions: List[str]


AnalyzeResponse = AnalyzeSuccess | AnalyzeNotSuitable
