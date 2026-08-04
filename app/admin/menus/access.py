from fastapi import Request
from sqlmodel import Session, select

from app.admin.dependencies import CurrentAdmin
from app.admin.models import AdminUser
from app.admin.rbac.constants import ROLE_SUPER_ADMIN
from app.admin.rbac.models import (
    AdminMenuApi,
    AdminRole,
    AdminRoleMenuApi,
)
from app.deps import CurrentSession
from app.libs.exceptions import AppError
from app.libs.redis import redis_client

""" 加缓存 """

""" reids存版本号 """
MENU_API_RULES_VER_KEY = "py_fisher_admin:menu_api_rules:ver"
# 本地：(redis版本号, 规则列表)
_menu_api_rules_cache: tuple[int, list[tuple[int, str, str]]] | None = None


# 读取redis版本号
def _get_rules_version() -> int:
    """读 Redis 版本；key 不存在视为 0。"""
    raw = redis_client.get(MENU_API_RULES_VER_KEY)
    return int(raw) if raw is not None else 0


# 写库成功后调用：版本 +1，并清掉当前进程本地缓存。
def invalidate_menu_api_rules_cache() -> None:
    """写库成功后调用：版本 +1，并清掉当前进程本地缓存。"""
    global _menu_api_rules_cache
    redis_client.incr(MENU_API_RULES_VER_KEY)
    _menu_api_rules_cache = None


def _load_menu_api_rules(session: Session) -> list[tuple[int, str, str]]:
    global _menu_api_rules_cache
    ver = _get_rules_version()
    if _menu_api_rules_cache is not None and _menu_api_rules_cache[0] == ver:
        return _menu_api_rules_cache[1]
    rows = session.exec(
        select(
            AdminMenuApi.id,
            AdminMenuApi.method,
            AdminMenuApi.path_pattern,
        ).where(AdminMenuApi.is_deleted == 0)
    ).all()
    rules = [(int(r[0]), str(r[1]), str(r[2])) for r in rows]
    _menu_api_rules_cache = (ver, rules)
    return rules


# (method, path) 精确白名单；method 用大写，path 与 request.url.path 一致
API_WHITELIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("GET", "/admin/ping"),
        ("POST", "/admin/login"),
        ("GET", "/admin/profile"),
        ("GET", "/admin/menus/userMenu"),
    }
)

"""
超管放行
白名单放行
命中 admin_menu_api（可多条）→ 角色拥有其中任一条即可
/** 只匹配子路径，不含 prefix 本身
* 通配符，匹配任意一段
未命中任何规则 → 403
"""


# 匹配路径
# def _match_pattern(path: str, pattern: str) -> bool:
#     if pattern.endswith("/**"):
#         prefix = pattern[:-3]  # 去掉 /**
#         # 只匹配 /admin/users/xxx，不再匹配 /admin/users 本身
#         return path.startswith(prefix + "/")
#     return path == pattern
def _match_pattern(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path.startswith(prefix + "/")

    if "*" in pattern:
        # 按 / 分段；* 仅匹配恰好一段
        path_parts = [p for p in path.split("/") if p != ""]
        pat_parts = [p for p in pattern.split("/") if p != ""]
        # 保留前导 / 的语义：两边都从绝对路径拆，空段已去掉
        # 要求：pattern 与 path 都以 / 开头时，段数一致
        if not pattern.startswith("/") or not path.startswith("/"):
            return False
        if len(path_parts) != len(pat_parts):
            return False
        for pp, pat in zip(path_parts, pat_parts):
            if pat == "*":
                continue
            if pp != pat:
                return False
        return True

    return path == pattern


# 查找匹配的菜单API
# def _find_matching_menu_apis(
#     session: Session, method: str, path: str
# ) -> list[AdminMenuApi]:
#     rows = session.exec(select(AdminMenuApi).where(AdminMenuApi.is_deleted == 0)).all()
#     hits: list[AdminMenuApi] = []
#     for row in rows:
#         if row.method != "*" and row.method.upper() != method:
#             continue
#         if _match_pattern(path, row.path_pattern):
#             hits.append(row)
#     return hits


def _find_matching_menu_api_ids(session: Session, method: str, path: str) -> list[int]:
    rules = _load_menu_api_rules(session)
    hits: list[int] = []
    for api_id, rule_method, path_pattern in rules:
        if rule_method != "*" and rule_method.upper() != method:
            continue
        if _match_pattern(path, path_pattern):
            hits.append(api_id)
    return hits


# 角色是否拥有命中集合中任一条
def _role_has_any_menu_api(
    session: Session, role_code: str, menu_api_ids: list[int]
) -> bool:
    if not menu_api_ids:
        return False
    row = session.exec(
        select(AdminRoleMenuApi.menu_api_id)
        .join(AdminRole, AdminRole.id == AdminRoleMenuApi.role_id)
        .where(
            AdminRole.code == role_code,
            AdminRole.is_deleted == 0,
            AdminRoleMenuApi.menu_api_id.in_(menu_api_ids),
        )
    ).first()
    return row is not None


def require_menu_api(
    request: Request,
    current_admin: CurrentAdmin,
    session: CurrentSession,
) -> AdminUser:
    if current_admin.role == ROLE_SUPER_ADMIN:
        return current_admin
    method = request.method.upper()
    path = request.url.path
    if (method, path) in API_WHITELIST:
        return current_admin

    # hits = _find_matching_menu_apis(session, method, path)
    # if not hits:
    #     raise AppError("未配置接口权限", code=403, http_status=403)

    # hit_ids = [h.id for h in hits if h.id is not None]
    # if not _role_has_any_menu_api(session, current_admin.role, hit_ids):
    #     raise AppError("无权限访问该接口", code=403, http_status=403)
    hit_ids = _find_matching_menu_api_ids(session, method, path)

    if not hit_ids:
        raise AppError("未配置接口权限", code=403, http_status=403)
    if not _role_has_any_menu_api(session, current_admin.role, hit_ids):
        raise AppError("无权限访问该接口", code=403, http_status=403)
    return current_admin
