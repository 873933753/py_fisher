from fastapi import Depends, Request

from app.admin.dependencies import CurrentAdmin
from app.admin.models import AdminUser
from app.admin.rbac.constants import ROLE_SUPER_ADMIN
from app.admin.rbac.models import AdminMenuApi, AdminRole, AdminRoleMenu
from app.deps import CurrentSession
from app.libs.exceptions import AppError
from sqlmodel import Session, col, select

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
命中 admin_menu_api → 角色须有对应 role_menu
未命中任何规则 → 403
 """


# 匹配路径
def _match_pattern(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]  # 去掉 /**
        # /admin/users/** 匹配 /admin/users 与 /admin/users/xxx
        return path == prefix or path.startswith(prefix + "/")
    return path == pattern


# 查找匹配的菜单ID
def _find_matching_menu_id(session: Session, method: str, path: str) -> int | None:
    rows = session.exec(select(AdminMenuApi).where(AdminMenuApi.is_deleted == 0)).all()
    hits: list[AdminMenuApi] = []
    for row in rows:
        if row.method != "*" and row.method.upper() != method:
            continue
        if _match_pattern(path, row.path_pattern):
            hits.append(row)
    if not hits:
        return None
    # 更长的 pattern 优先
    hits.sort(key=lambda r: len(r.path_pattern), reverse=True)
    return hits[0].menu_id


# 检查角色是否具备菜单权限
def _role_has_menu(session: Session, role_code: str, menu_id: int) -> bool:
    row = session.exec(
        select(AdminRoleMenu.menu_id)
        .join(AdminRole, AdminRole.id == AdminRoleMenu.role_id)
        .where(
            AdminRole.code == role_code,
            AdminRole.is_deleted == 0,
            AdminRoleMenu.menu_id == menu_id,
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

    menu_id = _find_matching_menu_id(session, method, path)
    if menu_id is None:
        raise AppError("未配置接口权限", code=403, http_status=403)

    if not _role_has_menu(session, current_admin.role, menu_id):
        raise AppError("无权限访问该接口", code=403, http_status=403)

    return current_admin
