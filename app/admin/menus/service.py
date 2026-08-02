from sqlmodel import Session, col, select

from app.admin.menus.schemas import (
    ALLOWED_METHODS,
    MenuApiItem,
    MenuApisOut,
    MenuApisPutIn,
    MenuCreateIn,
    MenuItem,
    MenuTreeNode,
    MenuUpdateIn,
    RoleMenuIdsIn,
    RoleMenuIdsOut,
)
from app.admin.models import AdminUser
from app.admin.rbac.constants import ROLE_SUPER_ADMIN
from app.admin.rbac.models import (
    AdminMenu,
    AdminMenuApi,
    AdminPermission,
    AdminRole,
    AdminRoleMenu,
)
from app.admin.rbac.service import _get_role_or_404
from app.database import auto_commit
from app.libs.exceptions import AppError


# 构建菜单树
def build_menu_tree(menus: list[AdminMenu]) -> list[MenuTreeNode]:
    nodes = {
        m.id: MenuTreeNode(
            id=m.id,
            parent_id=m.parent_id,
            title=m.title,
            path=m.path,
            component=m.component,
            icon=m.icon,
            sort=m.sort,
            menu_type=m.menu_type,
            permission_code=m.permission_code,
            children=[],
        )
        for m in menus
    }
    roots: list[MenuTreeNode] = []
    for node in nodes.values():
        if node.parent_id is not None and node.parent_id in nodes:
            nodes[node.parent_id].children.append(node)
        else:
            roots.append(node)

    def sort_rec(items: list[MenuTreeNode]) -> None:
        items.sort(key=lambda x: (x.sort, x.id))
        for it in items:
            sort_rec(it.children)

    sort_rec(roots)
    return roots


# 获取所有菜单树
def get_all_menu_tree(session: Session) -> list[MenuTreeNode]:
    menus = session.exec(
        select(AdminMenu)
        .where(AdminMenu.is_deleted == 0)
        .order_by(AdminMenu.sort, AdminMenu.id)
    ).all()
    return build_menu_tree(menus)


# 获取角色菜单id集合
def get_role_menu_ids(session: Session, role_code: str) -> RoleMenuIdsOut:
    role = _get_role_or_404(session, role_code)
    # 超管：配置页可展示「全部已存在菜单 id」，或返回全部 id 方便前端全勾禁用
    if role_code == ROLE_SUPER_ADMIN:
        ids = session.exec(
            select(AdminMenu.id).where(AdminMenu.is_deleted == 0).order_by(AdminMenu.id)
        ).all()
        return RoleMenuIdsOut(role_code=role_code, menu_ids=list(ids))
    rows = session.exec(
        select(AdminRoleMenu.menu_id).where(AdminRoleMenu.role_id == role.id)
    ).all()
    return RoleMenuIdsOut(role_code=role_code, menu_ids=sorted(rows))


# 设置角色菜单id集合
def set_role_menu_ids(
    session: Session,
    role_code: str,
    body: RoleMenuIdsIn,
) -> RoleMenuIdsOut:
    if role_code == ROLE_SUPER_ADMIN:
        raise AppError("超级管理员菜单不可修改")
    role = _get_role_or_404(session, role_code)
    wanted = sorted(set(body.menu_ids))
    if wanted:
        found = session.exec(
            select(AdminMenu).where(
                col(AdminMenu.id).in_(wanted),
                AdminMenu.is_deleted == 0,
            )
        ).all()
        found_ids = {m.id for m in found}
        missing = set(wanted) - found_ids
        if missing:
            raise AppError(f"无效菜单 id: {', '.join(map(str, sorted(missing)))}")
    else:
        found = []
    # 第一期：前端勾啥存啥；不自动补父目录
    with auto_commit(session):
        old = session.exec(
            select(AdminRoleMenu).where(AdminRoleMenu.role_id == role.id)
        ).all()
        for row in old:
            session.delete(row)
        for menu in found:
            session.add(AdminRoleMenu(role_id=role.id, menu_id=menu.id))
    return get_role_menu_ids(session, role_code)


""" 菜单项的增删改查 """


def _get_menu_or_404(session: Session, menu_id: int) -> AdminMenu:
    menu = session.get(AdminMenu, menu_id)
    if menu is None or menu.is_deleted != 0:
        raise AppError("菜单不存在", code=404, http_status=404)
    return menu


def _validate_parent(
    session: Session, parent_id: int | None, *, self_id: int | None = None
) -> None:
    if parent_id is None:
        return
    if self_id is not None and parent_id == self_id:
        raise AppError("父菜单不能是自己")
    parent = _get_menu_or_404(session, parent_id)
    # 可选：禁止挂到自己的子孙下（第一期可只做「不能是自己」）
    _ = parent


def _validate_permission_code(session: Session, code: str | None) -> None:
    if not code:
        return
    exists = session.exec(
        select(AdminPermission.id).where(
            AdminPermission.code == code,
            AdminPermission.is_deleted == 0,
        )
    ).first()
    if exists is None:
        raise AppError(f"无效权限码: {code}")


def get_menu(session: Session, menu_id: int) -> MenuItem:
    return MenuItem.model_validate(_get_menu_or_404(session, menu_id))


def create_menu(session: Session, body: MenuCreateIn) -> MenuItem:
    _validate_parent(session, body.parent_id)
    _validate_permission_code(session, body.permission_code)
    # directory 建议 path/component 可空；menu 建议有 path（可只 warning 不强制）
    with auto_commit(session):
        menu = AdminMenu(**body.model_dump())
        session.add(menu)
        session.flush()
        session.refresh(menu)
    return MenuItem.model_validate(menu)


def update_menu(session: Session, menu_id: int, body: MenuUpdateIn) -> MenuItem:
    menu = _get_menu_or_404(session, menu_id)
    data = body.model_dump(exclude_unset=True)

    if "parent_id" in data:
        _validate_parent(session, data["parent_id"], self_id=menu_id)
    if "permission_code" in data:
        _validate_permission_code(session, data["permission_code"])

    with auto_commit(session):
        for k, v in data.items():
            setattr(menu, k, v)
        session.add(menu)
        # commit 之前调用了 refresh，会丢掉尚未 flush 的改动，再从数据库 SELECT
        # 库里仍是 0 → 内存被刷回 sort=0
        # session.refresh(menu)
    return MenuItem.model_validate(menu)


def delete_menu(session: Session, menu_id: int) -> None:
    menu = _get_menu_or_404(session, menu_id)
    child = session.exec(
        select(AdminMenu.id).where(
            AdminMenu.parent_id == menu_id,
            AdminMenu.is_deleted == 0,
        )
    ).first()
    if child is not None:
        raise AppError("请先删除子菜单")

    with auto_commit(session):
        # 清角色绑定
        binds = session.exec(
            select(AdminRoleMenu).where(AdminRoleMenu.menu_id == menu_id)
        ).all()
        for row in binds:
            session.delete(row)
        menu.soft_delete()  # 若你们 AdminBaseModel 有该方法；否则 menu.is_deleted = 1


""" 侧栏用：仅登录，该接口仅校验登录，不校验权限 """


def get_menu_tree_for_admin(session: Session, admin: AdminUser) -> list[MenuTreeNode]:
    if admin.role == ROLE_SUPER_ADMIN:
        menus = session.exec(
            select(AdminMenu)
            .where(AdminMenu.is_deleted == 0)
            .order_by(AdminMenu.sort, AdminMenu.id)
        ).all()
        return build_menu_tree(menus)

    menus = session.exec(
        select(AdminMenu)
        .join(AdminRoleMenu, AdminRoleMenu.menu_id == AdminMenu.id)
        .join(AdminRole, AdminRole.id == AdminRoleMenu.role_id)
        .where(
            AdminRole.code == admin.role,
            AdminRole.is_deleted == 0,
            AdminMenu.is_deleted == 0,
        )
        .order_by(AdminMenu.sort, AdminMenu.id)
    ).all()

    # 侧栏只按 role_menu，不再用 permission_code 过滤
    return build_menu_tree(menus)


# def _prune_empty_directories(nodes: list[MenuTreeNode]) -> list[MenuTreeNode]:
#     out: list[MenuTreeNode] = []
#     for n in nodes:
#         n.children = _prune_empty_directories(n.children)
#         if n.menu_type == "directory" and not n.children:
#             continue
#         out.append(n)
#     return out


""" 菜单-绑定接口关联 """


def _normalize_method(method: str) -> str:
    m = method.strip().upper()
    if m not in ALLOWED_METHODS:
        raise AppError(f"无效 method: {method}")
    return m


def _normalize_path_pattern(path: str) -> str:
    p = path.strip()
    if not p.startswith("/"):
        raise AppError("path_pattern 必须以 / 开头")
    # 可选：要求以 /admin 开头
    return p


def list_menu_apis(session: Session, menu_id: int) -> MenuApisOut:
    _get_menu_or_404(session, menu_id)
    rows = session.exec(
        select(AdminMenuApi)
        .where(AdminMenuApi.menu_id == menu_id, AdminMenuApi.is_deleted == 0)
        .order_by(AdminMenuApi.sort, AdminMenuApi.id)
    ).all()
    return MenuApisOut(
        menu_id=menu_id,
        apis=[MenuApiItem.model_validate(r) for r in rows],
    )


def set_menu_apis(session: Session, menu_id: int, body: MenuApisPutIn) -> MenuApisOut:
    _get_menu_or_404(session, menu_id)

    normalized: list[tuple[str, str, int]] = []
    seen: set[tuple[str, str]] = set()
    for i, item in enumerate(body.apis):
        method = _normalize_method(item.method)
        path = _normalize_path_pattern(item.path_pattern)
        key = (method, path)
        if key in seen:
            raise AppError(f"重复接口: {method} {path}")
        seen.add(key)
        normalized.append((method, path, item.sort if item.sort else i))

    # 全局唯一：同一 method+path 不能挂在别的未删菜单上
    if normalized:
        paths = [p for _, p, _ in normalized]
        # methods = [m for m, _, _ in normalized]
        others = session.exec(
            select(AdminMenuApi).where(
                AdminMenuApi.is_deleted == 0,
                AdminMenuApi.menu_id != menu_id,
                col(AdminMenuApi.path_pattern).in_(paths),
            )
        ).all()
        for row in others:
            if (row.method, row.path_pattern) in seen:
                raise AppError(
                    f"接口已被菜单 {row.menu_id} 占用: {row.method} {row.path_pattern}"
                )

    with auto_commit(session):
        old = session.exec(
            select(AdminMenuApi).where(
                AdminMenuApi.menu_id == menu_id,
                AdminMenuApi.is_deleted == 0,
            )
        ).all()
        for row in old:
            row.soft_delete()  # 或 session.delete(row)；与项目习惯一致

        for method, path, sort in normalized:
            session.add(
                AdminMenuApi(
                    menu_id=menu_id,
                    method=method,
                    path_pattern=path,
                    sort=sort,
                )
            )

    return list_menu_apis(session, menu_id)
