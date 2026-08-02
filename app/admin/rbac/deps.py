from collections.abc import Callable

from app.admin.dependencies import AdminSession, CurrentAdmin
from app.admin.models import AdminUser
from app.admin.rbac.service import role_has_permission_db
from app.libs.exceptions import AppError


# 检查角色是否具备权限，返回AdminUser
def require_permissions(*codes: str) -> Callable[..., AdminUser]:
    if not codes:
        raise ValueError("require_permissions 至少需要一个权限码")

    def _checker(
        admin: CurrentAdmin,
        session: AdminSession,
    ) -> AdminUser:
        for code in codes:
            # 调用角色权限检查服务，看是否具备权限
            if not role_has_permission_db(session, admin.role, code):
                raise AppError("无权限", code=403, http_status=403)
        return admin

    return _checker
