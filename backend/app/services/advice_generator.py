from typing import Dict, List

from app.utils.safe_text import sanitize_text


DISCLAIMER = "该结果仅基于当前照片的面部比例、图像质量和上镜表现进行分析，不代表现实中的绝对颜值。"


def generate_advantages(score_data: Dict) -> List[str]:
    dims = score_data["dimensions"]
    items: List[str] = []
    if dims["face_proportion"]["score"] >= 19:
        items.append("面部整体比例在当前照片中较自然")
    if dims["face_contour"]["score"] >= 15:
        items.append("脸型轮廓与左右平衡呈现较稳定")
    if dims["feature_harmony"]["score"] >= 19:
        items.append("五官分布和整体匹配度较协调")
    if dims["skin_and_state"]["score"] >= 11:
        items.append("当前照片中的皮肤明度和气色表现较干净")
    if dims["photogenic_expression"]["score"] >= 12:
        items.append("当前照片的角度、光线和构图对上镜表现较友好")
    if not items:
        items.append("当前照片可以作为基础形象参考，但建议结合更清晰的正脸照片复核")
    return [sanitize_text(item) for item in items]


def generate_suggestions(score_data: Dict) -> List[str]:
    dims = score_data["dimensions"]
    suggestions: List[str] = []
    if score_data["photo_quality"]["score"] < 82:
        suggestions.append("建议使用自然光或均匀柔光，减少过暗、过曝和压缩模糊")
    if dims["face_proportion"]["score"] < 18:
        suggestions.append("建议使用正脸、镜头略高于眼睛的位置，减少俯拍或仰拍带来的比例变化")
    if dims["face_contour"]["score"] < 15:
        suggestions.append("发型可以适当增加头顶蓬松度，并减少脸侧遮挡，让轮廓更清晰")
    if dims["feature_harmony"]["score"] < 18:
        suggestions.append("拍摄时可增强眼神光，保持表情放松，让眼鼻唇区域更清晰")
    if not suggestions:
        suggestions.append("保持当前光线和角度，再根据场景微调发型、表情和背景统一度")
    return [sanitize_text(item) for item in suggestions]


def not_suitable_suggestions() -> List[str]:
    return [
        "请上传正脸照片",
        "请避免强遮挡、墨镜、口罩或大面积刘海遮住五官",
        "请使用自然光或均匀光线",
        "请避免过度美颜、过度压缩或模糊照片",
    ]
