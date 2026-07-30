from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlmodel import Session

from app.admin.models import AdminUser
from app.admin.security import decode_admin_access_token
from app.database import get_session
from app.libs.exceptions import AppError

# OAuth2PasswordBearer - FastAPI 提供的 OAuth2「密码模式 + Bearer Token」安全类
admin_oauth2_scheme = OAuth2PasswordBearer(
    # tokenUrl 指向后台登录，方便 Swagger 调试。在 /docs 里点 Authorize 时，Swagger 会知道去哪个地址换 token
    tokenUrl="/admin/login",
    auto_error=False,  # 设为 False 后：没有 token 时 不抛异常，而是返回 None，自己处理。
)

AdminSession = Annotated[Session, Depends(get_session)]
# AdminToken = Annotated[str | None, Depends(admin_oauth2_scheme)]

# 使用 Bearer Token 认证
admin_bearer_scheme = HTTPBearer(auto_error=False)
AdminToken = Annotated[str | None, Depends(admin_bearer_scheme)]


def get_current_admin(
    # token: AdminToken,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(admin_bearer_scheme)
    ],
    session: AdminSession,
) -> AdminUser:
    token = credentials.credentials if credentials else None
    if not token:
        raise AppError("未登录或登录已过期", code=401, http_status=401)

    admin_id = decode_admin_access_token(token)
    if admin_id is None:
        raise AppError("未登录或登录已过期", code=401, http_status=401)

    admin = session.get(AdminUser, admin_id)
    # 软删除已由 session_filters 处理；get 有时不走同一套 criteria，建议再判一次
    if admin is None or admin.is_deleted != 0:
        raise AppError("用户不存在", code=401, http_status=401)

    return admin


# 依赖注入到需要登录的路由
CurrentAdmin = Annotated[AdminUser, Depends(get_current_admin)]
