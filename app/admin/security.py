import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.secure import settings

# 根据type区域前后台的token类型
ADMIN_TOKEN_TYPE = "admin_access_token"
ADMIN_REFRESH_TOKEN_TYPE = "admin_refresh_token"  # 用于刷新token


def create_admin_access_token(admin_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(admin_id),
        "type": ADMIN_TOKEN_TYPE,
        "exp": expire,
        "jti": uuid.uuid4().hex,  # jwt id
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


# 解码管理员访问令牌
# 解码需要从token取出jti，用于查redis黑名单
def decode_admin_access_token(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != ADMIN_TOKEN_TYPE:
            return None
        jti = payload.get("jti")
        if not jti:
            # 旧 token 无 jti：视为无效，逼用户重新登录
            return None
        return {
            "admin_id": int(payload["sub"]),  # 建议用 admin_id，别用 sub，读代码更直观
            "jti": jti,
            "exp": payload.get("exp"),  # unix 时间戳（秒）
        }
    except jwt.PyJWTError:
        return None


""" refresh token """


# 创建refresh token
def create_admin_refresh_token(admin_id: int) -> tuple[str, str]:
    """签发 refresh；返回 (token, jti)，jti 用于写入 Redis。"""
    jti = uuid.uuid4().hex
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_EXPIRE_DAYS
    )
    payload = {
        "sub": str(admin_id),
        "type": ADMIN_REFRESH_TOKEN_TYPE,
        "exp": expire,
        "jti": jti,
    }
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token, jti


# 解码refresh token
def decode_admin_refresh_token(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != ADMIN_REFRESH_TOKEN_TYPE:
            return None
        jti = payload.get("jti")
        if not jti:
            return None
        return {
            "admin_id": int(payload["sub"]),
            "jti": jti,
            "exp": payload.get("exp"),
        }
    except jwt.PyJWTError:
        return None
