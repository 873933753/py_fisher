from datetime import datetime, timedelta, timezone

import jwt

from app.secure import settings

# 根据type区域前后台的token类型
ADMIN_TOKEN_TYPE = "admin_access_token"


def create_admin_access_token(admin_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(admin_id),
        "type": ADMIN_TOKEN_TYPE,
        "exp": expire,
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_admin_access_token(token: str | None) -> int | None:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != ADMIN_TOKEN_TYPE:
            return None
        return int(payload["sub"])
    except jwt.PyJWTError:
        return None
