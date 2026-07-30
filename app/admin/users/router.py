from fastapi import APIRouter

from app.admin.auth.schemas import ApiResponse  # 共用响应壳；列表 schema 下一步再写
from app.admin.dependencies import CurrentAdmin
from app.admin.users.schemas import FrontUserDetail
from app.admin.users.service import get_front_user, list_front_users
from app.deps import CurrentSession
from app.schemas.pagination import Page, PageSize
from app.setting import DEFAULT_PAGE_SIZE

users_router = APIRouter(tags=["admin-users"])


@users_router.get("/ping", response_model=ApiResponse[dict])
def users_ping(current_admin: CurrentAdmin):
    return ApiResponse(data={"ok": True}, message="users ok")


# 用户列表
@users_router.get("")
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
