from typing import Annotated

from fastapi import Path
from sqlmodel import select

from app.deps.common import CurrentSession, CurrentUser
from app.libs.exceptions import AppError
from app.models.wish import Wish


def get_own_active_wish_from_path(
    wish_id: Annotated[int, Path(ge=1)],
    session: CurrentSession,
    current_user: CurrentUser,
) -> Wish:
    wish = session.exec(
        select(Wish).where(
            Wish.id == wish_id,
            Wish.user_id == current_user.id,
            Wish.launched == False,
        )
    ).first()

    if not wish:
        raise AppError("无法撤销")

    return wish
