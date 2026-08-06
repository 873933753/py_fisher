from app.libs.redis import redis_client

""" refresh token 存储到redis """
# key: admin_refresh:jti
# value: admin_id
# ttl: refresh 剩余秒数
ADMIN_REFRESH_REDIS_KEY = "admin_refresh_token:"


def admin_refresh_key(jti: str) -> str:
    return f"{ADMIN_REFRESH_REDIS_KEY}{jti}"


def store_admin_refresh(jti: str, admin_id: int, ttl_seconds: int) -> None:
    """登录/刷新成功后写入；ttl 与 refresh JWT 寿命对齐。"""
    if ttl_seconds <= 0:
        return
    redis_client.set(admin_refresh_key(jti), str(admin_id), ex=ttl_seconds)


def get_admin_refresh_admin_id(jti: str) -> int | None:
    raw = redis_client.get(admin_refresh_key(jti))
    return int(raw) if raw is not None else None


def delete_admin_refresh(jti: str) -> None:
    redis_client.delete(admin_refresh_key(jti))


""" 增加黑名单，用于退出登录 """
#  logout 拉黑access，防止被重复使用
ADMIN_ACCESS_BLACKLIST_KEY = "admin_access_blacklist:"


def admin_access_blacklist_key(jti: str) -> str:
    return f"{ADMIN_ACCESS_BLACKLIST_KEY}{jti}"


# 黑名单时效：ttl_seconds 是 access token 剩余寿命，即access过期了就将黑名单删除
# 否则redis内存爆炸
def blacklist_admin_access(jti: str, ttl_seconds: int) -> None:
    """登出：拉黑 access jti，TTL = 剩余寿命。"""
    if ttl_seconds <= 0:
        return
    redis_client.set(admin_access_blacklist_key(jti), "1", ex=ttl_seconds)


def is_admin_access_blacklisted(jti: str) -> bool:
    return redis_client.exists(admin_access_blacklist_key(jti)) == 1
