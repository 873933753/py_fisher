from fastapi import APIRouter, Depends, Body
from app.libs.auth import get_current_user
from typing import Annotated
from app.schemas.response import ApiResponse
from app.models.gift import Gift
from app.forms.drift import DriftForm
from app.models.drift import Drift
from app.view_models.drift import DriftCollectionViewModel
from app.schemas.pagination import PageData
from app.schemas.drift import DriftItem
from app.schemas.pagination import DEFAULT_PAGE_SIZE, paginate

from app.deps import (
    CurrentSession,
    CurrentUser,
    get_waiting_drift_as_requester,
    get_waiting_drift_as_gifter,
    get_mailable_drift_as_gifter,
    get_requestable_gift_from_query,
    get_requestable_gift_from_drift_form,
    can_send_dependency,
)

from app.services.drift import (
    confirm_mailed,
    create_drift_request,
    redraw_drift_request,
    request_reject_service,
)

drift_router = APIRouter(
    prefix="/drift",
    dependencies=[Depends(get_current_user)],
)


# 索要逻辑===============================================
# 判断能否索要：
# 1. 自己的礼物不能索要
# 2、鱼豆要 > 1
# 3、每索取两个商品必须送出一本
@drift_router.get("/can_request", response_model=ApiResponse[dict])
def can_request(
    current_gift: Annotated[Gift, Depends(get_requestable_gift_from_query)],
):
    # 返回用信息信用等
    user = current_gift.user.summary

    return ApiResponse(data=user, message="可以索要")


# 提交索要表单
@drift_router.post("/save_drift", response_model=ApiResponse[dict])
def save_drift(
    form: DriftForm,
    current_gift: Annotated[Gift, Depends(get_requestable_gift_from_drift_form)],
    session: CurrentSession,
    current_user: CurrentUser,
):
    create_drift_request(session, form, current_user, current_gift)
    return ApiResponse(data={}, message="索要成功，请等待对方确认")


# 交易记录列表====================================
@drift_router.post("/drift_list", response_model=ApiResponse[PageData[DriftItem]])
def drift_list(
    session: CurrentSession,
    current_user: CurrentUser,
    page: Annotated[int, Body(ge=1, le=999)] = 1,
    size: Annotated[int, Body(ge=1, le=999)] = DEFAULT_PAGE_SIZE,
):
    stmt = Drift.get_drift_list(current_user.id)
    drifts, total = paginate(session, stmt, page, size)
    items = DriftCollectionViewModel(drifts, current_user.id).items
    return ApiResponse(
        data=PageData.build(items, total, page, size),
    )


# 撤销索要 - status为1可撤销
@drift_router.post("/request/redraw", response_model=ApiResponse[dict])
def request_redraw(
    drift: Annotated[Drift, Depends(get_waiting_drift_as_requester)],
    session: CurrentSession,
    current_user: CurrentUser,
):
    redraw_drift_request(session, drift, current_user)
    return ApiResponse(data={}, message="撤销成功")


# 拒绝索要 - status为1可拒绝
@drift_router.post("/request/reject", response_model=ApiResponse[dict])
def request_reject(
    drift: Annotated[Drift, Depends(get_waiting_drift_as_gifter)],
    session: CurrentSession,
):
    request_reject_service(session, drift)
    return ApiResponse(data={}, message="拒绝成功")


# 确认已邮寄 mailed
@drift_router.post("/request/mailed/{drift_id}", response_model=ApiResponse[dict])
def request_mailed(
    drift: Annotated[Drift, Depends(get_mailable_drift_as_gifter)],
    session: CurrentSession,
    current_user: CurrentUser,
):
    confirm_mailed(session, drift, current_user)
    return ApiResponse(data={}, message="确认成功")


# 向他赠送逻辑===============================================
@drift_router.get("/can_send", response_model=ApiResponse[dict])
def give(
    _can_send: Annotated[None, Depends(can_send_dependency)],
):

    # 成功 - 给该用户发送请求页的邮件进项申请
    return ApiResponse(data={}, message="可以赠送")
