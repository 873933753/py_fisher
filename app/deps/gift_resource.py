from fastapi import Path
from typing import Annotated
from sqlmodel import select
from app.deps.common import CurrentSession, CurrentUser
from app.libs.exceptions import AppError
from app.models.gift import Gift


def get_own_active_gift_from_path(
    gift_id: Annotated[int, Path(ge=1)],
    session: CurrentSession,
    current_user: CurrentUser,
) -> Gift:
    gift = session.exec(
        select(Gift).where(
            Gift.id == gift_id,
            Gift.user_id == current_user.id,
            Gift.launched == False,
        )
    ).first()

    if not gift:
        raise AppError("无法撤销")

    return gift
