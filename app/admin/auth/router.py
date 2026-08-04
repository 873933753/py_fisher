from fastapi import APIRouter

# create_app 已 include admin_router，会间接加载
from app.admin.auth.schemas import (
    AdminInfo,
    AdminLoginIn,
    AdminLoginResult,
    ApiResponse,
)
from app.admin.auth.service import login_admin
from app.admin.dependencies import CurrentAdmin
from app.deps import CurrentSession

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
