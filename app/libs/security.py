import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from app.secure import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES


# 密码加密
def hash_password(plain: str) -> str:
    # gensalt() 生成随机盐；hashpw 返回 bytes，入库存 str
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


# 密码验证
def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8"),
    )


# 生成访问令牌
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),  # subject，放用户 id
        "type": "access_token",  # 区分登录 JWT
        "exp": expire,  # 过期时间
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


# 解码访问令牌
def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        # 校验类型，防止重置密码token被用其他token解析，这里只能解析登录token
        if payload.get("type") != "access_token":
            return None
        return int(payload["sub"])
    except jwt.PyJWTError:
        return None


# 生成重置密码token
# 参数：用户id，过期时间（默认10分钟）
def create_reset_token(user_id: int, expiration: int = 300) -> str:
    import uuid

    jti = uuid.uuid4().hex
    expire = datetime.now(timezone.utc) + timedelta(seconds=expiration)
    payload = {
        "sub": str(user_id),
        "type": "reset_password",  # 区分登录 JWT
        "exp": expire,
        "jti": jti,  # 唯一标识，防止重放攻击
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    # return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, jti


def decode_reset_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "reset_password":
            return None
        return int(payload["sub"]), payload["jti"]
    except jwt.PyJWTError:
        return None
