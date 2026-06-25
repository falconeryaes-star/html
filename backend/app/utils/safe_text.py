FORBIDDEN_WORDS = [
    "丑",
    "难看",
    "缺陷",
    "畸形",
    "失败",
    "拉胯",
    "崩",
    "低级",
    "土",
    "不正常",
]


REPLACEMENTS = {
    "丑": "当前照片表现不理想",
    "难看": "当前照片表现不理想",
    "缺陷": "可优化项",
    "畸形": "比例受照片条件影响",
    "失败": "不稳定",
    "拉胯": "表现受影响",
    "崩": "不稳定",
    "低级": "不够统一",
    "土": "风格不够统一",
    "不正常": "不够稳定",
}


def sanitize_text(text: str) -> str:
    output = text
    for word, replacement in REPLACEMENTS.items():
        output = output.replace(word, replacement)
    return output


def contains_forbidden(text: str) -> bool:
    return any(word in text for word in FORBIDDEN_WORDS)
