from fastapi import APIRouter

from app.admin.auth.schemas import ApiResponse  # 共用响应壳；列表 schema 下一步再写
from app.admin.dependencies import CurrentAdmin
from app.admin.users.schemas import FrontUserDetail, FrontUserUpdateIn
from app.admin.users.service import (
    delete_front_user,
    get_front_user,
    list_front_users,
    update_front_user,
)
from app.deps import CurrentSession
from app.schemas.pagination import Page, PageSize
from app.setting import DEFAULT_PAGE_SIZE

users_router = APIRouter(tags=["admin-users"])


@users_router.get(
    "/ping",
    response_model=ApiResponse[dict],
    summary="前台用户模块健康检查",
)
def users_ping(current_admin: CurrentAdmin):
    return ApiResponse(data={"ok": True}, message="users ok")


@users_router.get("", summary="前台用户列表")
def users_list(
    current_admin: CurrentAdmin,
    session: CurrentSession,
    page: Page = 1,
    size: PageSize = DEFAULT_PAGE_SIZE,
    keyword: str | None = None,
):
    data = list_front_users(session, page=page, size=size, keyword=keyword)
    return ApiResponse(data=data, message="ok")


# 用户详情
@users_router.get(
    "/{user_id}",
    response_model=ApiResponse[FrontUserDetail],
    summary="前台用户详情",
)
def users_detail(
    user_id: int,
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    return ApiResponse(data=get_front_user(session, user_id), message="ok")


# 更新用户信息
@users_router.patch(
    "/{user_id}",
    # response_model=ApiResponse[FrontUserDetail],
    response_model=ApiResponse[None],
    summary="更新前台用户",
)
def users_update(
    user_id: int,
    body: FrontUserUpdateIn,
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    update_front_user(session, user_id, body)
    return ApiResponse(
        # data=update_front_user(session, user_id, body),
        data=None,
        message="更新成功",
    )


# 删除用户
@users_router.delete(
    "/{user_id}",
    response_model=ApiResponse[None],
    summary="软删除前台用户",
)
def users_delete(
    user_id: int,
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    delete_front_user(session, user_id)
    return ApiResponse(data=None, message="删除成功")
