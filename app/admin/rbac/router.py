from fastapi import APIRouter

from app.admin.auth.schemas import ApiResponse
from app.admin.menus.router import menus_router
from app.admin.rbac.schemas import RoleCreateIn, RoleItem, RoleUpdateIn
from app.admin.rbac.service import (
    create_role,
    delete_role,
    list_roles,
    update_role,
)
from app.deps import CurrentSession

rbac_router = APIRouter(tags=["admin-rbac"])


@rbac_router.get("/ping", response_model=ApiResponse[dict])
def rbac_ping():
    return ApiResponse(data={"ok": True}, message="rbac ok")


@rbac_router.get(
    "/roles", response_model=ApiResponse[list[RoleItem]], summary="角色列表"
)
def rbac_roles(session: CurrentSession):
    return ApiResponse(data=list_roles(session), message="ok")


""" 角色的创建和修改 """


@rbac_router.post(
    "/roles/create",
    response_model=ApiResponse[RoleItem],
    summary="创建角色",
)
def rbac_role_create(body: RoleCreateIn, session: CurrentSession):
    return ApiResponse(data=create_role(session, body), message="创建成功")


@rbac_router.patch(
    "/roles/update/{role_code}",
    response_model=ApiResponse[RoleItem],
    summary="更新角色",
)
def rbac_role_update(
    role_code: str,
    body: RoleUpdateIn,
    session: CurrentSession,
):
    return ApiResponse(
        data=update_role(session, role_code, body),
        message="更新成功",
    )


@rbac_router.delete(
    "/roles/delete/{role_code}",
    response_model=ApiResponse[None],
    summary="删除角色",
)
def rbac_role_delete(role_code: str, session: CurrentSession):
    delete_role(session, role_code)
    return ApiResponse(data=None, message="删除成功")


# menu还是挂在rbac_router下
rbac_router.include_router(menus_router)
