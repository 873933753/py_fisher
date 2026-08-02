from sqlmodel import Session, col, select

from app.admin.rbac.constants import ROLE_SUPER_ADMIN
from app.admin.rbac.models import (
    AdminPermission,
    AdminRole,
    AdminRolePermission,
)
from app.admin.rbac.schemas import (
    PermissionItem,
    RoleItem,
    RolePermissionCodesIn,
    RolePermissionCodesOut,
)
from app.database import auto_commit
from app.libs.exceptions import AppError


# 加载角色权限码，返回权限码集合
def load_permission_codes(session: Session, role_code: str) -> frozenset[str]:
    """
    根据角色 code 加载权限码。
    super_admin 返回 {"*"}，与现有一致。
    """
    if role_code == ROLE_SUPER_ADMIN:
        return frozenset({"*"})

    stmt = (
        select(AdminPermission.code)
        .join(
            AdminRolePermission,
            col(AdminRolePermission.permission_id) == col(AdminPermission.id),
        )
        .join(
            AdminRole,
            col(AdminRole.id) == col(AdminRolePermission.role_id),
        )
        .where(
            AdminRole.code == role_code,
            AdminRole.is_deleted == 0,
            AdminPermission.is_deleted == 0,
        )
    )
    # 软删过滤对 AdminBaseModel 一般已生效；显式写上更直观
    rows = session.exec(stmt).all()
    # 返回角色拥有的权限码集合
    return frozenset(rows)


# 检查角色是否具备权限，返回bool
def role_has_permission_db(session: Session, role_code: str, code: str) -> bool:
    perms = load_permission_codes(session, role_code)
    # 超级管理员拥有全部权限
    if "*" in perms:
        return True
    # 非超管，检查角色是否具备权限
    return code in perms


# 获取客户端可用的权限码列表,给前端用即权限列表
def list_permission_codes_for_client(session: Session, role_code: str) -> list[str]:
    codes = load_permission_codes(session, role_code)
    if "*" in codes:
        rows = session.exec(
            select(AdminPermission.code).where(AdminPermission.is_deleted == 0)
        ).all()
        # sorted排序，返回列表
        return sorted(rows)
    return sorted(codes)


# 获取角色列表
def list_roles(session: Session) -> list[RoleItem]:
    rows = session.exec(
        select(AdminRole).where(AdminRole.is_deleted == 0).order_by(AdminRole.id)
    ).all()
    return [RoleItem.model_validate(r) for r in rows]


# 获取权限列表
def list_permissions(
    session: Session,
    *,
    group_name: str | None = None,
) -> list[PermissionItem]:
    stmt = select(AdminPermission).where(AdminPermission.is_deleted == 0)
    if group_name:
        stmt = stmt.where(AdminPermission.group_name == group_name)
    stmt = stmt.order_by(AdminPermission.group_name, AdminPermission.id)
    rows = session.exec(stmt).all()
    return [PermissionItem.model_validate(r) for r in rows]


""" 角色权限的修改 """
# 先获取当前角色的权限，然后修改新权限


# 获取角色或404
def _get_role_or_404(session: Session, role_code: str) -> AdminRole:
    role = session.exec(
        select(AdminRole).where(
            AdminRole.code == role_code,
            AdminRole.is_deleted == 0,
        )
    ).first()
    if role is None:
        raise AppError("角色不存在", code=404, http_status=404)
    return role


# 获取角色权限码列表
def get_role_permission_codes(
    session: Session, role_code: str
) -> RolePermissionCodesOut:
    _get_role_or_404(session, role_code)
    codes = list_permission_codes_for_client(session, role_code)
    return RolePermissionCodesOut(role_code=role_code, codes=codes)


# 修改角色权限
def set_role_permission_codes(
    session: Session,
    role_code: str,
    body: RolePermissionCodesIn,
) -> RolePermissionCodesOut:
    if role_code == ROLE_SUPER_ADMIN:
        raise AppError("超级管理员权限不可修改")
    role = _get_role_or_404(session, role_code)
    wanted = sorted(set(body.codes))
    if wanted:
        found = session.exec(
            select(AdminPermission).where(
                col(AdminPermission.code).in_(wanted),
                AdminPermission.is_deleted == 0,
            )
        ).all()
        found_codes = {p.code for p in found}
        missing = set(wanted) - found_codes
        if missing:
            raise AppError(f"无效权限码: {', '.join(sorted(missing))}")
    else:
        found = []
    with auto_commit(session):
        old = session.exec(
            select(AdminRolePermission).where(AdminRolePermission.role_id == role.id)
        ).all()
        for row in old:
            session.delete(row)
        for perm in found:
            session.add(AdminRolePermission(role_id=role.id, permission_id=perm.id))
    return get_role_permission_codes(session, role_code)
