from app.admin.security import (
    create_admin_access_token,
    create_admin_refresh_token,
    decode_admin_access_token,
    decode_admin_refresh_token,
)

""" 
测 app/admin/security.py 的编解码与类型隔离
刷新/登出依赖 type + jti；混用 token 必须返回 None，否则权限会串
"""


def test_access_token_roundtrip():
    token = create_admin_access_token(42)
    data = decode_admin_access_token(token)
    assert data is not None
    assert data["admin_id"] == 42
    assert data["jti"]  # 非空


def test_refresh_token_roundtrip():
    token, jti = create_admin_refresh_token(7)
    data = decode_admin_refresh_token(token)
    assert data is not None
    assert data["admin_id"] == 7
    assert data["jti"] == jti


def test_access_decode_rejects_refresh_token():
    token, _ = create_admin_refresh_token(1)
    assert decode_admin_access_token(token) is None


def test_refresh_decode_rejects_access_token():
    token = create_admin_access_token(1)
    assert decode_admin_refresh_token(token) is None


def test_decode_empty_returns_none():
    assert decode_admin_access_token(None) is None
    assert decode_admin_access_token("") is None
