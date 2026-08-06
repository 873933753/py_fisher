from sqlmodel import Session, select

from app.admin.models import AdminUser
from app.admin.rbac.constants import ROLE_SUPER_ADMIN
from app.admin.rbac.models import AdminRole, AdminRoleMenu, AdminRoleMenuApi
from app.admin.rbac.schemas import RoleCreateIn, RoleItem, RoleUpdateIn
from app.database import auto_commit
from app.libs.exceptions import AppError


# 获取角色列表
def list_roles(session: Session) -> list[RoleItem]:
    rows = session.exec(
        select(AdminRole).where(AdminRole.is_deleted == 0).order_by(AdminRole.id)
    ).all()
    return [RoleItem.model_validate(r) for r in rows]


""" 角色权限的修改 """


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


# 校验角色是否存在
def _require_role_code(session, role_code: str) -> AdminRole:
    return _get_role_or_404(session, role_code.strip().lower())


""" 角色的创建和修改 """


def create_role(session, body: RoleCreateIn) -> RoleItem:
    code = body.code.strip().lower()
    # 可选：re.fullmatch(r"[a-z][a-z0-9_]{0,31}", code)
    exists = session.exec(select(AdminRole).where(AdminRole.code == code)).first()
    if exists:
        raise AppError("角色码已存在")
    with auto_commit(session):
        role = AdminRole(code=code, name=body.name.strip())
        session.add(role)
        session.flush()
        session.refresh(role)
    return RoleItem.model_validate(role)


def update_role(session, role_code: str, body: RoleUpdateIn) -> RoleItem:
    role = _get_role_or_404(session, role_code)
    data = body.model_dump(exclude_unset=True)
    if not data:
        return RoleItem.model_validate(role)
    with auto_commit(session):
        if "name" in data and data["name"] is not None:
            role.name = data["name"].strip()
        session.add(role)
    return RoleItem.model_validate(role)


def delete_role(session, role_code: str) -> None:
    if role_code == ROLE_SUPER_ADMIN:
        raise AppError("不能删除超级管理员角色")
    role = _get_role_or_404(session, role_code)

    # 仍有账号在用
    used = session.exec(
        select(AdminUser.id).where(AdminUser.role == role.code).limit(1)
    ).first()
    if used is not None:
        raise AppError("仍有账号使用该角色，无法删除")

    with auto_commit(session):
        for row in session.exec(
            select(AdminRoleMenuApi).where(AdminRoleMenuApi.role_id == role.id)
        ).all():
            session.delete(row)
        for row in session.exec(
            select(AdminRoleMenu).where(AdminRoleMenu.role_id == role.id)
        ).all():
            session.delete(row)
        session.delete(role)
