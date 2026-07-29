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


# 健康检查接口
@auth_router.get("/ping", response_model=ApiResponse[dict])
def admin_ping():
    return ApiResponse(data={"ok": True}, message="admin ok")


# 登录接口
@auth_router.post("/login", response_model=ApiResponse[AdminLoginResult])
def admin_login(body: AdminLoginIn, session: CurrentSession):
    result = login_admin(session, body)
    return ApiResponse(data=result, message="登录成功")


# 获取当前用户信息接口
@auth_router.get("/profile", response_model=ApiResponse[AdminInfo])
def admin_profile(current_admin: CurrentAdmin):
    return ApiResponse(data=AdminInfo.model_validate(current_admin))
