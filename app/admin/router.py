from fastapi import APIRouter, Depends

import app.admin.session_filters  # noqa: F401
from app.admin.admins.router import admins_router
from app.admin.auth.router import auth_router
from app.admin.menus.router import user_menus_router
from app.admin.rbac.router import rbac_router
from app.admin.uploads.router import uploads_router
from app.admin.users.router import users_router
from app.admin.menus.access import require_menu_api

admin_router = APIRouter()
admin_router.include_router(auth_router)  # login/profile 在白名单
# 其他路由需要菜单api权限
admin_router.include_router(
    users_router, prefix="/users", dependencies=[Depends(require_menu_api)]
)
admin_router.include_router(
    uploads_router, prefix="/uploads", dependencies=[Depends(require_menu_api)]
)
admin_router.include_router(
    admins_router, prefix="/admins", dependencies=[Depends(require_menu_api)]
)
admin_router.include_router(
    rbac_router, prefix="/rbac", dependencies=[Depends(require_menu_api)]
)
admin_router.include_router(
    user_menus_router, prefix="/menus", dependencies=[Depends(require_menu_api)]
)
