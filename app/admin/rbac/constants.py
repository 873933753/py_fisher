# 角色码（与 admin_user.role 取值一致）
ROLE_SUPER_ADMIN = "super_admin"
ROLE_OPERATOR = "operator"

# 权限码：{资源}:{动作}
# PERM_USER_LIST = "user:list"
# PERM_USER_DETAIL = "user:detail"
# PERM_USER_UPDATE = "user:update"
# PERM_USER_DELETE = "user:delete"

# PERM_ADMIN_LIST = "admin:list"
# PERM_ADMIN_CREATE = "admin:create"
# PERM_ADMIN_UPDATE = "admin:update"
# PERM_ADMIN_DELETE = "admin:delete"

# PERM_UPLOAD_IMAGE = "upload:image"

PERM_USER_MANAGE = "user:manage"
PERM_ADMIN_MANAGE = "admin:manage"
PERM_UPLOAD_MANAGE = "upload:manage"

PERM_RBAC_MANAGE = "rbac:manage"

# 运营默认权限（可按业务再改）
# OPERATOR_PERMISSIONS: frozenset[str] = frozenset(
#     {
#         PERM_USER_LIST,
#         PERM_USER_DETAIL,
#         PERM_UPLOAD_IMAGE,
#     }
# )

# # 角色 → 权限集合；超管用 "*" 表示全部
# ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
#     ROLE_SUPER_ADMIN: frozenset({"*"}),
#     ROLE_OPERATOR: OPERATOR_PERMISSIONS,
# }


# def permissions_for_role(role: str) -> frozenset[str]:
#     return ROLE_PERMISSIONS.get(role, frozenset())


# def role_has_permission(role: str, code: str) -> bool:
#     perms = permissions_for_role(role)
#     if "*" in perms:
#         return True
#     return code in perms
