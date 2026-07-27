from typing import Annotated

from fastapi import Body, Path, Query
from sqlmodel import select

from app.deps.common import CurrentSession, CurrentUser
from app.libs.enums import DriftStatus
from app.libs.exceptions import AppError
from app.models.drift import Drift
from app.models.gift import Gift
from app.forms.drift import DriftForm
from app.models.wish import Wish


# 可以撤销的索要的依赖判断
# 1）所属当前用户、2）当前状态为等待中
# 3）所属drift_id
def get_waiting_drift_as_requester(
    drift_id: Annotated[int, Body(embed=True, ge=1)],
    session: CurrentSession,
    current_user: CurrentUser,
) -> Drift:
    drift = session.exec(
        select(Drift).where(
            Drift.id == drift_id,
            Drift.requester_id == current_user.id,
        )
    ).first()

    if not drift:
        raise AppError("交易不存在")

    if drift.status != DriftStatus.Waiting:
        raise AppError("当前状态不能撤销")

    return drift


# 可以拒绝的索要的依赖判断
# 1）所属当前用户、2）当前状态为等待中
# 3）所属drift_id
def get_waiting_drift_as_gifter(
    drift_id: Annotated[int, Body(embed=True, ge=1)],
    session: CurrentSession,
    current_user: CurrentUser,
) -> Drift:
    drift = session.exec(
        select(Drift).where(
            Drift.id == drift_id,
            Drift.gifter_id == current_user.id,
        )
    ).first()
    if not drift:
        raise AppError("交易不存在")
    if drift.status != DriftStatus.Waiting:
        raise AppError("当前状态不能拒绝")
    return drift


# 可以点击确认邮寄的依赖判断
# 1）所属当前用户、2）当前状态为等待中
# 3）所属drift_id
def get_mailable_drift_as_gifter(
    drift_id: Annotated[int, Path(ge=1)],  # Path - 路径参数,ge - 大于等于1
    session: CurrentSession,
    current_user: CurrentUser,
) -> Drift:
    drift = session.exec(
        select(Drift).where(
            Drift.id == drift_id,
            Drift.gifter_id == current_user.id,
            Drift.status == DriftStatus.Waiting,
        )
    ).first()

    if not drift:
        raise AppError("当前状态不能邮寄")

    return drift


# 确保可以索要的依赖判断
# 1、自己的书不能索要
# 2、鱼豆要 > 1
# 3、每索取两边必须送出一本
def _get_requestable_gift(
    session: CurrentSession,
    current_user: CurrentUser,
    gift_id: int,
) -> Gift:
    # gift = session.get(Gift, gift_id)
    gift = session.exec(
        select(Gift).where(
            Gift.id == gift_id,
            Gift.launched == False,  # 过滤已赠送的礼物
        )
    ).first()

    if not gift:
        raise AppError("礼物不存在")

    if gift.is_yourself_gift(current_user.id):
        raise AppError("不能索要自己的书")

    if not current_user.can_request_gift_beans():
        raise AppError("鱼豆不足")

    if not current_user.can_request_gift_more(session):
        raise AppError("每索取两边必须送出一本")

    return gift


# can_request 用 query 版本
def get_requestable_gift_from_query(
    gift_id: Annotated[int, Query(ge=1)],
    session: CurrentSession,
    current_user: CurrentUser,
) -> Gift:
    return _get_requestable_gift(session, current_user, gift_id)


# save_drift 用 form 版本
def get_requestable_gift_from_drift_form(
    form: DriftForm,
    session: CurrentSession,
    current_user: CurrentUser,
) -> Gift:
    return _get_requestable_gift(session, current_user, form.gift_id)


# 确保可以赠送的依赖判断
def can_send_dependency(
    isbn: Annotated[str, Query(min_length=1)],
    wish_id: Annotated[int, Query(ge=1)],
    session: CurrentSession,
    current_user: CurrentUser,
) -> None:
    gift = session.exec(
        select(Gift).where(
            Gift.user_id == current_user.id,
            Gift.isbn == isbn,
            Gift.launched == False,
        )
    ).first()

    if not gift:
        raise AppError("无法赠送")

    wish = session.exec(
        select(Wish).where(
            Wish.isbn == isbn,
            Wish.launched == False,
            Wish.id == wish_id,
        )
    ).first()

    if not wish:
        raise AppError("心愿不存在")
