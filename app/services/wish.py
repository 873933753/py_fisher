from sqlmodel import Session

from app.database import auto_commit
from app.models.wish import Wish

from app.libs.exceptions import AppError
from app.models.user import User


def redraw_wish(
    session: Session,
    wish: Wish,
) -> None:
    with auto_commit(session):
        wish.soft_delete()


def add_wish_to_list_service(
    session: Session,
    current_user: User,
    isbn: str,
) -> Wish:
    if not current_user.can_save_to_list(session, isbn):
        raise AppError(message="这个商品已在赠送清单或心愿清单中，请不要重复添加")

    wish = Wish(
        user_id=current_user.id,
        isbn=isbn,
    )

    with auto_commit(session):
        session.add(wish)

    return wish
