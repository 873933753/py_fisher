from sqlmodel import Session, col, or_, select

from app.admin.users.schemas import FrontUserDetail, FrontUserItem, FrontUserUpdateIn
from app.database import auto_commit
from app.libs.exceptions import AppError
from app.models.user import User
from app.schemas.pagination import PageData, paginate
from app.secure import oss_settings
from app.setting import DEFAULT_PAGE_SIZE


# 用户列表
def list_front_users(
    session: Session,
    *,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
    keyword: str | None = None,
) -> PageData[FrontUserItem]:
    # 查询用户列表,按id降序
    stmt = (
        select(User)
        .order_by(col(User.id).desc())
        # 包含软删除的数据
        .execution_options(include_deleted=True)
    )

    if keyword:
        kw = keyword.strip()
        if kw:
            # 模糊查询
            pattern = f"%{kw}%"
            stmt = stmt.where(
                or_(  # 或查询
                    col(User.email).like(pattern),
                    col(User.nickname).like(pattern),
                )
            )

    users, total = paginate(session, stmt, page, size, include_deleted=True)
    items = [FrontUserItem.model_validate(u) for u in users]
    return PageData.build(items, total, page, size)


# 获取用户或404,用于内部调用
def _get_user_or_404(session: Session, user_id: int) -> User:
    user = session.exec(
        select(User).where(User.id == user_id).execution_options(include_deleted=True)
    ).first()
    if user is None:
        raise AppError("用户不存在", code=404, http_status=404)
    return user


# 获取前台用户详情
def get_front_user(session: Session, user_id: int) -> FrontUserDetail:
    return FrontUserDetail.model_validate(_get_user_or_404(session, user_id))


# 更新前台用户信息
def update_front_user(
    session: Session,
    user_id: int,
    body: FrontUserUpdateIn,
) -> None:
    user = _get_user_or_404(session, user_id)
    data = body.model_dump(exclude_unset=True)

    # 布尔禁用 → 库内软删标记
    if "is_disabled" in data:
        disabled = data.pop("is_disabled")
        if disabled is True:
            user.is_deleted = 1
        elif disabled is False:
            user.is_deleted = 0

    # 如果手机号为空，则删除手机号
    if "phone_number" in data and not data["phone_number"]:
        data.pop("phone_number")

    # 手机号唯一（有值且变更时）
    if "phone_number" in data:
        phone = data["phone_number"]
        if phone:
            exists = session.exec(
                select(User)
                .where(User.phone_number == phone, User.id != user_id)
                .execution_options(include_deleted=True)
            ).first()
            if exists:
                raise AppError("手机号已被占用")

    # 头像校验，如果传了头像，则校验是否是合法的OSS地址
    if "avatar" in data and data["avatar"]:
        base = oss_settings.OSS_PUBLIC_BASE_URL
        if not str(data["avatar"]).startswith(base + "/"):
            raise AppError("头像地址非法")

    for key, value in data.items():
        setattr(user, key, value)
    # 更新更新时间
    # user.update_time_now()
    with auto_commit(session):
        session.add(user)

    # return FrontUserDetail.model_validate(user)


# 删除前台用户
def delete_front_user(session: Session, user_id: int) -> None:
    user = _get_user_or_404(session, user_id)
    if user.is_deleted != 0:
        raise AppError("用户不存在")  # 或直接幂等 return
    with auto_commit(session):
        user.soft_delete()
        session.add(user)
