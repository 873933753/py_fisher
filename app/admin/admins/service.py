from sqlmodel import Session, col, select

from app.admin.admins.schemas import (
    AdminAccountCreateIn,
    AdminAccountItem,
    AdminAccountUpdateIn,
)
from app.admin.models import AdminUser
from app.database import auto_commit
from app.libs.exceptions import AppError
from app.libs.security import hash_password
from app.schemas.pagination import PageData, paginate
from app.setting import DEFAULT_PAGE_SIZE


def list_admin_accounts(
    session: Session,
    # * 关键字参数，表示后面的参数都是关键字参数，可以不传
    *,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
    keyword: str | None = None,
) -> PageData[AdminAccountItem]:
    stmt = (
        select(AdminUser)
        .order_by(col(AdminUser.id).desc())
        .execution_options(include_deleted=True)
    )
    if keyword:
        kw = keyword.strip()
        if kw:
            stmt = stmt.where(col(AdminUser.phone_number).like(f"%{kw}%"))

    rows, total = paginate(session, stmt, page, size, include_deleted=True)
    items = [AdminAccountItem.model_validate(r) for r in rows]
    return PageData.build(items, total, page, size)


# 判断当前身份
def _get_admin_or_404(session: Session, admin_id: int) -> AdminUser:
    admin = session.exec(
        select(AdminUser)
        .where(AdminUser.id == admin_id)
        .execution_options(include_deleted=True)
    ).first()
    if admin is None:
        raise AppError("管理员不存在", code=404, http_status=404)
    return admin


def get_admin_account(session: Session, admin_id: int) -> AdminAccountItem:
    return AdminAccountItem.model_validate(_get_admin_or_404(session, admin_id))


# 添加后台账号
def create_admin_account(
    session: Session,
    body: AdminAccountCreateIn,
) -> AdminAccountItem:
    exists = session.exec(
        select(AdminUser)
        .where(AdminUser.phone_number == body.phone_number)
        .execution_options(include_deleted=True)
    ).first()
    if exists:
        # 含已软删：表上 unique，占着号就不能再建
        raise AppError("手机号已被占用")
    admin = AdminUser(
        phone_number=body.phone_number,
        password_hash=hash_password(body.password),
    )
    with auto_commit(session):
        session.add(admin)
    return AdminAccountItem.model_validate(admin)


# 更新后台账号
def update_admin_account(
    session: Session,
    admin_id: int,
    body: AdminAccountUpdateIn,
    *,
    current_admin_id: int,
) -> AdminAccountItem:
    admin = _get_admin_or_404(session, admin_id)
    data = body.model_dump(exclude_unset=True)
    # 不能禁用自己（避免把自己锁出后台）
    if data.get("is_disabled") is True and admin_id == current_admin_id:
        raise AppError("不能禁用当前登录账号")
    if "is_disabled" in data:
        disabled = data.pop("is_disabled")
        if disabled is True:
            admin.is_deleted = 1
        elif disabled is False:
            admin.is_deleted = 0
    if "password" in data:
        plain = data.pop("password")
        if plain:
            admin.password_hash = hash_password(plain)
    if "phone_number" in data:
        phone = data["phone_number"]
        exists = session.exec(
            select(AdminUser)
            .where(AdminUser.phone_number == phone, AdminUser.id != admin_id)
            .execution_options(include_deleted=True)
        ).first()
        if exists:
            raise AppError("手机号已被占用")
        admin.phone_number = phone
        data.pop("phone_number", None)
    # 一般不应再有剩余字段；若有可 setattr
    for key, value in data.items():
        setattr(admin, key, value)
    with auto_commit(session):
        session.add(admin)
    return AdminAccountItem.model_validate(admin)


# 删除后台账号
def delete_admin_account(
    session: Session,
    admin_id: int,
    *,
    current_admin_id: int,
) -> None:
    if admin_id == current_admin_id:
        raise AppError("不能删除当前登录账号")
    admin = _get_admin_or_404(session, admin_id)
    if admin.is_deleted != 0:
        raise AppError("账号已删除")
    with auto_commit(session):
        admin.soft_delete()
        session.add(admin)
