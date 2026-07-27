from functools import lru_cache
from typing import Generator

import redis
from redis import Redis

from app.secure import REDIS_URL


@lru_cache
def get_redis_client() -> Redis:
    """进程内单例，避免每次请求新建连接。"""
    return redis.from_url(
        REDIS_URL,
        decode_responses=True,  # 存取都是 str，验证码更方便
    )


# 模块级别名，auth.py 里可直接 import
redis_client = get_redis_client()


def get_redis() -> Generator[Redis, None, None]:
    """FastAPI 依赖注入，用法类似 Depends(get_session)。"""
    client = get_redis_client()
    yield client


# 验证码缓存key
def reset_password_code_key(user_id: int) -> str:
    return f"reset_password_code:{user_id}"


# 同一邮箱发送验证码冷却时间key
def reset_password_send_limit_key(email: str) -> str:
    return f"reset_password_send_limit:{email}"
