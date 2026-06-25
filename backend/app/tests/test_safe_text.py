from app.utils.safe_text import contains_forbidden, sanitize_text


def test_sanitize_removes_forbidden_words():
    text = sanitize_text("这个缺陷会导致照片难看")
    assert contains_forbidden(text) is False
