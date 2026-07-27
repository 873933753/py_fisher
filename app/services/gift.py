from sqlmodel import Session

from app.database import auto_commit
from app.models.gift import Gift
from app.models.user import User
from app.setting import BEAN_PER_GIFT
from app.libs.exceptions import AppError


def redraw_gift(
    session: Session,
    gift: Gift,
    current_user: User,
) -> None:
    with auto_commit(session):
        gift.soft_delete()
        current_user.beans -= BEAN_PER_GIFT


# 添加商品到赠送清单
def add_gift_to_list_service(
    session: Session,
    current_user: User,
    isbn: str,
) -> Gift:
    if not current_user.can_save_to_list(session, isbn):
        raise AppError(message="这个商品已在赠送清单或心愿清单中，请不要重复添加")

    gift = Gift(
        user_id=current_user.id,
        isbn=isbn,
    )

    with auto_commit(session):
        session.add(gift)
        current_user.beans += BEAN_PER_GIFT

    return gift
