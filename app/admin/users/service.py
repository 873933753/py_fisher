from sqlmodel import Session, col, or_, select

from app.admin.users.schemas import FrontUserDetail, FrontUserItem
from app.libs.exceptions import AppError
from app.models.user import User
from app.schemas.pagination import PageData, paginate
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


# 用户详情
def get_front_user(session: Session, user_id: int) -> FrontUserDetail:
    user = session.exec(
        select(User).where(User.id == user_id).execution_options(include_deleted=True)
    ).first()
    if user is None:
        raise AppError("用户不存在", code=404, http_status=404)
    return FrontUserDetail.model_validate(user)
