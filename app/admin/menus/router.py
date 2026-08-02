from fastapi import APIRouter

from app.admin.auth.schemas import ApiResponse
from app.admin.menus.schemas import (
    MenuCreateIn,
    MenuItem,
    MenuTreeNode,
    MenuUpdateIn,
    RoleMenuIdsIn,
    RoleMenuIdsOut,
)
from app.admin.menus.service import (
    MenuApisOut,
    MenuApisPutIn,
    create_menu,
    delete_menu,
    get_all_menu_tree,
    get_menu,
    get_menu_tree_for_admin,
    get_role_menu_ids,
    list_menu_apis,
    set_menu_apis,
    set_role_menu_ids,
    update_menu,
)
from app.deps import CurrentSession

menus_router = APIRouter(
    tags=["admin-menus"],
    # dependencies=[Depends(require_permissions(PERM_RBAC_MANAGE))],
)

""" 菜单管理 """


# 全量菜单树
@menus_router.get(
    "/menus/tree",
    response_model=ApiResponse[list[MenuTreeNode]],
    summary="全量菜单树（配置用）",
)
def rbac_menus_tree(session: CurrentSession):
    return ApiResponse(data=get_all_menu_tree(session), message="ok")


# 查询角色已绑菜单
@menus_router.get(
    "/roles/{role_code}/menus",
    response_model=ApiResponse[RoleMenuIdsOut],
    summary="查询角色已绑菜单",
)
def get_role_menus(role_code: str, session: CurrentSession):
    return ApiResponse(data=get_role_menu_ids(session, role_code), message="ok")


# 覆盖角色菜单
@menus_router.put(
    "/roles/{role_code}/menus",
    response_model=ApiResponse[RoleMenuIdsOut],
    summary="覆盖角色菜单",
)
def update_role_menus(
    role_code: str,
    body: RoleMenuIdsIn,
    session: CurrentSession,
):
    return ApiResponse(
        data=set_role_menu_ids(session, role_code, body),
        message="更新成功",
    )


""" 菜单项的增删改查 """


@menus_router.get(
    "/menus/{menu_id}",
    response_model=ApiResponse[MenuItem],
    summary="菜单详情",
)
def rbac_menu_detail(menu_id: int, session: CurrentSession):
    return ApiResponse(data=get_menu(session, menu_id), message="ok")


@menus_router.post(
    "/menus/create",
    response_model=ApiResponse[MenuItem],
    summary="创建菜单",
)
def rbac_menu_create(body: MenuCreateIn, session: CurrentSession):
    return ApiResponse(data=create_menu(session, body), message="创建成功")


@menus_router.patch(
    "/menus/update/{menu_id}",
    response_model=ApiResponse[MenuItem],
    summary="更新菜单",
)
def rbac_menu_update(menu_id: int, body: MenuUpdateIn, session: CurrentSession):
    return ApiResponse(data=update_menu(session, menu_id, body), message="更新成功")


@menus_router.delete(
    "/menus/delete/{menu_id}",
    response_model=ApiResponse[None],
    summary="软删除菜单",
)
def rbac_menu_delete(menu_id: int, session: CurrentSession):
    delete_menu(session, menu_id)
    return ApiResponse(data=None, message="删除成功")


# 侧栏用：仅登录，该接口仅校验登录，不校验权限
user_menus_router = APIRouter(tags=["admin-menus"])


@user_menus_router.get(
    "/userMenu",
    response_model=ApiResponse[list[MenuTreeNode]],
    summary="当前登录用户菜单树",
)
def user_menu_tree(
    current_admin: CurrentAdmin,
    session: CurrentSession,
):
    data = get_menu_tree_for_admin(session, current_admin)
    return ApiResponse(data=data, message="ok")


""" 菜单-绑定接口 """


@menus_router.get(
    "/menus/{menu_id}/apis",
    response_model=ApiResponse[MenuApisOut],
    summary="查询菜单已绑接口",
)
def menu_apis_get(menu_id: int, session: CurrentSession):
    return ApiResponse(data=list_menu_apis(session, menu_id), message="ok")


@menus_router.put(
    "/menus/{menu_id}/apis",
    response_model=ApiResponse[MenuApisOut],
    summary="覆盖菜单绑定接口",
)
def menu_apis_put(menu_id: int, body: MenuApisPutIn, session: CurrentSession):
    return ApiResponse(
        data=set_menu_apis(session, menu_id, body),
        message="更新成功",
    )
