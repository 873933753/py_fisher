from app.libs.oss import _detect_image_content_type


def test_detect_png():
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
    assert _detect_image_content_type(data) == "image/png"


def test_detect_jpeg():
    data = b"\xff\xd8\xff" + b"\x00" * 9
    assert _detect_image_content_type(data) == "image/jpeg"


def test_reject_plain_text():
    assert _detect_image_content_type(b"hello world!!!!") is None
