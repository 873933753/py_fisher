from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

# create_app 已 include admin_router，会间接加载
from app.admin.auth.schemas import (
    AdminInfo,
    AdminLoginIn,
    AdminLoginResult,
    AdminLogoutIn,
    AdminRefreshIn,
    AdminRefreshResult,
    ApiResponse,
)
from app.admin.auth.service import login_admin, logout_admin, refresh_admin_tokens
from app.admin.dependencies import CurrentAdmin, admin_bearer_scheme
from app.deps import CurrentSession
from app.libs.exceptions import AppError

auth_router = APIRouter(tags=["admin-auth"])


@auth_router.get(
    "/ping",
    response_model=ApiResponse[dict],
    summary="后台认证模块健康检查",
)
def admin_ping():
    return ApiResponse(data={"ok": True}, message="admin ok")


@auth_router.post(
    "/login",
    response_model=ApiResponse[AdminLoginResult],
    summary="后台管理员登录",
)
def admin_login(body: AdminLoginIn, session: CurrentSession):
    result = login_admin(session, body)
    return ApiResponse(data=result, message="登录成功")


@auth_router.get(
    "/profile",
    response_model=ApiResponse[AdminInfo],
    summary="获取当前管理员信息",
)
def admin_profile(current_admin: CurrentAdmin, session: CurrentSession):
    data = AdminInfo(
        id=current_admin.id,
        phone_number=current_admin.phone_number,
        role=current_admin.role,
    )
    return ApiResponse(data=data, message="ok")


@auth_router.post(
    "/refresh",
    response_model=ApiResponse[AdminRefreshResult],
    summary="刷新后台访问令牌",
)
def admin_refresh(body: AdminRefreshIn):
    result = refresh_admin_tokens(body.refreshToken)
    return ApiResponse(data=result, message="刷新成功")


@auth_router.post("/logout", response_model=ApiResponse[dict], summary="后台登出")
def admin_logout(
    body: AdminLogoutIn,  # refreshToken: str | None = None
    credentials: Annotated[  # 从请求头取出 Authorization
        HTTPAuthorizationCredentials | None,  # 参数类型：有凭证对象，或没有则为 None
        Depends(admin_bearer_scheme),  # 值怎么来：交给 HTTPBearer 去解析请求头
    ] = None,
):  # 有 Bearer 就取出 access token 字符串，没有就是 None
    token = credentials.credentials if credentials else None
    # 登出也需要登录态
    if not token:
        raise AppError("未登录或登录已过期", code=401, http_status=401)
    logout_admin(token, body.refreshToken)
    return ApiResponse(data={}, message="已登出")
