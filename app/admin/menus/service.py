from sqlmodel import Session, col, select

from app.admin.menus.access import invalidate_menu_api_rules_cache
from app.admin.menus.schemas import (
    ALLOWED_METHODS,
    MenuApiItem,
    MenuApisOut,
    MenuApisPutIn,
    MenuCreateIn,
    MenuItem,
    MenuTreeNode,
    MenuUpdateIn,
    RoleAccessIn,
    RoleAccessOut,
)
from app.admin.models import AdminUser
from app.admin.rbac.constants import ROLE_SUPER_ADMIN
from app.admin.rbac.models import (
    AdminMenu,
    AdminMenuApi,
    AdminRole,
    AdminRoleMenu,
    AdminRoleMenuApi,
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

    # 向上走：禁止把节点挂到自己的子孙下（否则成环）
    seen: set[int] = set()
    cur_id: int | None = parent_id
    while cur_id is not None:
        if self_id is not None and cur_id == self_id:
            raise AppError("不能将菜单移动到其子菜单下")
        if cur_id in seen:
            raise AppError("菜单父级关系异常")
        seen.add(cur_id)
        parent = _get_menu_or_404(session, cur_id)
        cur_id = parent.parent_id


def get_menu(session: Session, menu_id: int) -> MenuItem:
    return MenuItem.model_validate(_get_menu_or_404(session, menu_id))


def create_menu(session: Session, body: MenuCreateIn) -> MenuItem:
    _validate_parent(session, body.parent_id)
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

    with auto_commit(session):
        for k, v in data.items():
            setattr(menu, k, v)
        session.add(menu)
        # commit 之前调用了 refresh，会丢掉尚未 flush 的改动，再从数据库 SELECT
        # 库里仍是 0 → 内存被刷回 sort=0
        # session.refresh(menu)
    return MenuItem.model_validate(menu)


# 删除菜单，会清理该菜单下接口及角色接口绑定
# 菜单改硬删
def delete_menu(session: Session, menu_id: int) -> None:
    menu = _get_menu_or_404(session, menu_id)
    child = session.exec(
        select(AdminMenu.id).where(AdminMenu.parent_id == menu_id)
    ).first()
    # 若仍继承软删过滤，上面已自动只看到未删子节点；有子则拒
    if child is not None:
        raise AppError("请先删除子菜单")

    with auto_commit(session):
        apis = session.exec(
            select(AdminMenuApi)
            .where(AdminMenuApi.menu_id == menu_id)
            .execution_options(include_deleted=True)  # 清掉历史软删行
        ).all()
        api_ids = [a.id for a in apis if a.id is not None]

        if api_ids:
            for row in session.exec(
                select(AdminRoleMenuApi).where(
                    col(AdminRoleMenuApi.menu_api_id).in_(api_ids)
                )
            ).all():
                session.delete(row)

        for api in apis:
            session.delete(api)  # 硬删接口

        for row in session.exec(
            select(AdminRoleMenu).where(AdminRoleMenu.menu_id == menu_id)
        ).all():
            session.delete(row)

        session.delete(menu)  # 硬删菜单

    invalidate_menu_api_rules_cache()


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

    return build_menu_tree(menus)


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
    if "//" in p or (p.endswith("/") and p != "/"):
        raise AppError("path_pattern 格式无效")

    # /** 前缀通配：仅允许「字面前缀 + /**」
    if p.endswith("/**"):
        prefix = p[:-3]
        if not prefix or "*" in prefix:
            raise AppError("path_pattern 的 /** 前缀不能再包含 *")
        return p

    # 一段 * 通配：每一段须为字面量或单独的 *（禁止 roles* 这类）
    if "*" in p:
        parts = [seg for seg in p.split("/") if seg != ""]
        for seg in parts:
            if "*" in seg and seg != "*":
                raise AppError(
                    "path_pattern 中 * 只能单独成段（如 /admin/rbac/roles/*/access）"
                )
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


# 1) 规范化 + 本菜单内查重 (method, path)
# 2) 加载本菜单现有 API → by_id = {id: row}
# 3) 校验：body 里带的 id 必须在 by_id 中；同一 id 不能出现两次
# 4) 允许多个菜单挂相同 method+path（页面依赖清单）；鉴权按 menu_api_id 勾选
def set_menu_apis(session: Session, menu_id: int, body: MenuApisPutIn) -> MenuApisOut:
    """按 id 同步菜单 API 池：有 id 更新（保留角色勾选），无 id 新增，未提交的旧 id 删除。"""
    _get_menu_or_404(session, menu_id)

    existing = session.exec(
        select(AdminMenuApi)
        .where(AdminMenuApi.menu_id == menu_id)
        .execution_options(include_deleted=True)
    ).all()
    by_id: dict[int, AdminMenuApi] = {a.id: a for a in existing if a.id is not None}

    # (api_id|None, method, path, sort, remark)
    normalized: list[tuple[int | None, str, str, int, str | None]] = []
    seen_keys: set[tuple[str, str]] = set()
    seen_ids: set[int] = set()
    keep_ids: set[int] = set()

    for i, item in enumerate(body.apis):
        method = _normalize_method(item.method)
        path = _normalize_path_pattern(item.path_pattern)
        key = (method, path)
        if key in seen_keys:
            raise AppError(f"重复接口: {method} {path}")
        seen_keys.add(key)

        api_id = item.id
        if api_id is not None:
            if api_id in seen_ids:
                raise AppError(f"重复接口 id: {api_id}")
            if api_id not in by_id:
                raise AppError(f"接口不存在或不属于该菜单: {api_id}")
            seen_ids.add(api_id)
            keep_ids.add(api_id)

        normalized.append(
            (api_id, method, path, item.sort if item.sort else i, item.remark)
        )

    with auto_commit(session):
        # 5) 删除：旧 id 不在 keep_ids 里的
        remove_ids = [i for i in by_id if i not in keep_ids]
        if remove_ids:
            for row in session.exec(
                select(AdminRoleMenuApi).where(
                    col(AdminRoleMenuApi.menu_api_id).in_(remove_ids)
                )
            ).all():
                session.delete(row)
            session.flush()
            for rid in remove_ids:
                session.delete(by_id[rid])
            session.flush()
        # 6) 遍历 body.apis：
        #    if item.id: 更新 by_id[id] 的 method/path/sort/remark
        #    else: session.add(新 AdminMenuApi(...))
        for api_id, method, path, sort, remark in normalized:
            if api_id is not None:
                row = by_id[api_id]
                row.method = method
                row.path_pattern = path
                row.sort = sort
                row.remark = remark
                row.is_deleted = 0
                session.add(row)
            else:
                session.add(
                    AdminMenuApi(
                        menu_id=menu_id,
                        method=method,
                        path_pattern=path,
                        sort=sort,
                        remark=remark,
                    )
                )

    # return list_menu_apis(session, menu_id)
    invalidate_menu_api_rules_cache()
    return list_menu_apis(session, menu_id)


""" 角色-菜单-接口关联 """


def get_role_access(session: Session, role_code: str) -> RoleAccessOut:
    role = _get_role_or_404(session, role_code)

    if role_code == ROLE_SUPER_ADMIN:
        menu_ids = session.exec(
            select(AdminMenu.id).where(AdminMenu.is_deleted == 0).order_by(AdminMenu.id)
        ).all()
        api_ids = session.exec(
            select(AdminMenuApi.id)
            .where(AdminMenuApi.is_deleted == 0)
            .order_by(AdminMenuApi.id)
        ).all()
        return RoleAccessOut(
            role_code=role_code,
            menu_ids=list(menu_ids),
            menu_api_ids=list(api_ids),
        )

    menu_ids = session.exec(
        select(AdminRoleMenu.menu_id).where(AdminRoleMenu.role_id == role.id)
    ).all()
    api_ids = session.exec(
        select(AdminRoleMenuApi.menu_api_id).where(AdminRoleMenuApi.role_id == role.id)
    ).all()
    return RoleAccessOut(
        role_code=role_code,
        menu_ids=sorted(menu_ids),
        menu_api_ids=sorted(api_ids),
    )


def set_role_access(
    # session: Session, role_code: str, body: RoleAccessIn, admin: AdminUser
    session: Session,
    role_code: str,
    body: RoleAccessIn,
    admin: AdminUser,
    *,
    method: str | None = None,
    path: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> RoleAccessOut:
    if role_code == ROLE_SUPER_ADMIN:
        raise AppError("超级管理员授权不可修改")

    role = _get_role_or_404(session, role_code)
    wanted_menus = sorted(set(body.menu_ids))
    wanted_apis = sorted(set(body.menu_api_ids))

    # 校验菜单
    if wanted_menus:
        menus = session.exec(
            select(AdminMenu).where(
                col(AdminMenu.id).in_(wanted_menus),
                AdminMenu.is_deleted == 0,
            )
        ).all()
        found_menu_ids = {m.id for m in menus}
        missing = set(wanted_menus) - found_menu_ids
        if missing:
            raise AppError(f"无效菜单 id: {', '.join(map(str, sorted(missing)))}")
    else:
        found_menu_ids = set()

    # 校验 API：存在、未删，且所属菜单必须在 menu_ids 里
    if wanted_apis:
        apis = session.exec(
            select(AdminMenuApi).where(
                col(AdminMenuApi.id).in_(wanted_apis),
                AdminMenuApi.is_deleted == 0,
            )
        ).all()
        found_api_ids = {a.id for a in apis}
        missing = set(wanted_apis) - found_api_ids
        if missing:
            raise AppError(f"无效菜单接口 id: {', '.join(map(str, sorted(missing)))}")
        orphan = [a.id for a in apis if a.menu_id not in found_menu_ids]
        if orphan:
            raise AppError(f"接口未归属已选菜单: {', '.join(map(str, sorted(orphan)))}")
    else:
        apis = []
    # 记录变更前的数据
    before = get_role_access(session, role_code).model_dump()

    with auto_commit(session):
        # 覆盖菜单
        for row in session.exec(
            select(AdminRoleMenu).where(AdminRoleMenu.role_id == role.id)
        ).all():
            session.delete(row)
        for mid in found_menu_ids:
            session.add(AdminRoleMenu(role_id=role.id, menu_id=mid))

        # 覆盖 API
        for row in session.exec(
            select(AdminRoleMenuApi).where(AdminRoleMenuApi.role_id == role.id)
        ).all():
            session.delete(row)
        for api in apis:
            session.add(AdminRoleMenuApi(role_id=role.id, menu_api_id=api.id))

    # 业务成功后再记审计
    from app.admin.audit.service import write_audit

    # 记录变更后的数据
    after = get_role_access(session, role_code).model_dump()
    write_audit(
        session,
        operator=admin,
        module="menus",
        action="set_role_access",
        resource_type="role_access",
        resource_id=role.code,
        request_summary=body.model_dump(),
        before_summary=before,
        after_summary=after,
        success=True,
        # http 字段
        method=method,
        path=path,
        ip=ip,
        user_agent=user_agent,
    )
    return get_role_access(session, role_code)
