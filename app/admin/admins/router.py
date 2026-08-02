from fastapi import APIRouter

from app.admin.admins.schemas import (
    AdminAccountCreateIn,
    AdminAccountItem,
    AdminAccountUpdateIn,
)
from app.admin.admins.service import (
    create_admin_account,
    delete_admin_account,
    get_admin_account,
    list_admin_accounts,
    update_admin_account,
)
from app.admin.auth.schemas import ApiResponse
from app.admin.dependencies import CurrentAdmin

# from app.admin.rbac.constants import PERM_ADMIN_CREATE, PERM_ADMIN_UPDATE
from app.deps import CurrentSession
from app.schemas.pagination import Page, PageData, PageSize
from app.setting import DEFAULT_PAGE_SIZE

admins_router = APIRouter(
    tags=["admin-admins"],
    # 依赖：当前管理员须具备管理后台账号的权限
    # dependencies=[Depends(require_permissions(PERM_ADMIN_MANAGE))],
)


@admins_router.get(
    "/ping",
    response_model=ApiResponse[dict],
    summary="后台管理员模块健康检查",
)
def admins_ping(current_admin: CurrentAdmin):
    return ApiResponse(data={"ok": True}, message="admins ok")


# 后台用户列表
@admins_router.get(
    "",
    response_model=ApiResponse[PageData[AdminAccountItem]],
    summary="后台账号分页列表",
)
def admins_list(
    current_admin: CurrentAdmin,
    session: CurrentSession,
    page: Page = 1,
    size: PageSize = DEFAULT_PAGE_SIZE,
    keyword: str | None = None,
):
    data = list_admin_accounts(session, page=page, size=size, keyword=keyword)
    return ApiResponse(data=data, message="ok")


# 后台账号详情
@admins_router.get(
    "/{admin_id}",
    response_model=ApiResponse[AdminAccountItem],
    summary="后台账号详情",
)
def admins_detail(
    admin_id: int,
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    return ApiResponse(data=get_admin_account(session, admin_id), message="ok")


# 创建后台账号
@admins_router.post(
    "/create",
    response_model=ApiResponse[AdminAccountItem],
    summary="创建后台账号",
    # dependencies=[Depends(require_permissions(PERM_ADMIN_CREATE))],
)
def admins_create(
    body: AdminAccountCreateIn,
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    return ApiResponse(
        data=create_admin_account(session, body),
        message="创建成功",
    )


# 更新后台账号
@admins_router.patch(
    "/update/{admin_id}",
    response_model=ApiResponse[AdminAccountItem],
    summary="更新后台账号",
    # 依赖：当前管理员须具备更新后台账号的权限
    # dependencies=[Depends(require_permissions(PERM_ADMIN_UPDATE))],
)
def admins_update(
    admin_id: int,
    body: AdminAccountUpdateIn,
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    return ApiResponse(
        data=update_admin_account(
            session,
            admin_id,
            body,
            current_admin_id=current_admin.id,
        ),
        message="更新成功",
    )


# 删除后台账号
@admins_router.delete(
    "/delete/{admin_id}",
    response_model=ApiResponse[None],
    summary="软删除后台账号",
)
def admins_delete(
    admin_id: int,
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    delete_admin_account(
        session,
        admin_id,
        current_admin_id=current_admin.id,
    )
    return ApiResponse(data=None, message="删除成功")
