from fastapi import APIRouter

from app.admin.auth.schemas import ApiResponse
from app.admin.menus.router import menus_router
from app.admin.rbac.schemas import (
    PermissionItem,
    RoleItem,
    RolePermissionCodesIn,
    RolePermissionCodesOut,
)
from app.admin.rbac.service import (
    get_role_permission_codes,
    list_permissions,
    list_roles,
    set_role_permission_codes,
)
from app.deps import CurrentSession

rbac_router = APIRouter(
    tags=["admin-rbac"],
    # dependencies=[Depends(require_permissions(PERM_RBAC_MANAGE))],
)


@rbac_router.get("/ping", response_model=ApiResponse[dict])
def rbac_ping():
    return ApiResponse(data={"ok": True}, message="rbac ok")


@rbac_router.get(
    "/roles", response_model=ApiResponse[list[RoleItem]], summary="角色列表"
)
def rbac_roles(session: CurrentSession):
    return ApiResponse(data=list_roles(session), message="ok")


@rbac_router.get(
    "/permissions",
    response_model=ApiResponse[list[PermissionItem]],
    summary="权限列表",
)
def rbac_permissions(
    session: CurrentSession,
    group_name: str | None = None,
):
    return ApiResponse(
        data=list_permissions(session, group_name=group_name),
        message="ok",
    )


# 角色权限获取并修改
@rbac_router.get(
    "/roles/{role_code}/permissions",
    response_model=ApiResponse[RolePermissionCodesOut],
    summary="查询角色已绑权限",
    # dependencies=[Depends(require_permissions(PERM_RBAC_MANAGE))],
)
def rbac_role_permissions_get(role_code: str, session: CurrentSession):
    return ApiResponse(
        data=get_role_permission_codes(session, role_code),
        message="ok",
    )


@rbac_router.put(
    "/roles/{role_code}/permissions",
    response_model=ApiResponse[RolePermissionCodesOut],
    summary="覆盖角色权限",
    # dependencies=[Depends(require_permissions(PERM_RBAC_MANAGE))],
)
def rbac_role_permissions_put(
    role_code: str,
    body: RolePermissionCodesIn,
    session: CurrentSession,
):
    return ApiResponse(
        data=set_role_permission_codes(session, role_code, body),
        message="更新成功",
    )


# menu还是挂在rbac_router下
rbac_router.include_router(menus_router)
