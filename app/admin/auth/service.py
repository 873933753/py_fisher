import time

from sqlmodel import Session, select

from app.admin.auth.schemas import (
    AdminInfo,
    AdminLoginIn,
    AdminLoginResult,
    AdminRefreshResult,
)
from app.admin.auth.token_store import (
    blacklist_admin_access,
    delete_admin_refresh,
    get_admin_refresh_admin_id,
    store_admin_refresh,
)
from app.admin.models import AdminUser
from app.admin.security import (
    create_admin_access_token,
    create_admin_refresh_token,
    decode_admin_access_token,
    decode_admin_refresh_token,
)
from app.libs.exceptions import AppError
from app.libs.security import verify_password
from app.secure import settings


# 登录业务逻辑
def login_admin(session: Session, body: AdminLoginIn) -> AdminLoginResult:
    admin = session.exec(
        select(AdminUser).where(AdminUser.phone_number == body.phone_number)
    ).first()

    # 账号不存在与密码错误同一文案，降低枚举风险
    if not admin or not verify_password(body.password, admin.password_hash):
        raise AppError("手机号或密码错误")

    token = create_admin_access_token(admin.id)
    refresh_token, jti = create_admin_refresh_token(admin.id)
    store_admin_refresh(jti, admin.id, settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 60 * 60)

    info = AdminInfo(id=admin.id, phone_number=admin.phone_number, role=admin.role)
    return AdminLoginResult(
        token=token,
        refreshToken=refresh_token,
        userInfo=info,
    )


""" 换取新token和refresh """


def refresh_admin_tokens(refresh_token: str) -> AdminRefreshResult:
    decoded = decode_admin_refresh_token(refresh_token)
    if not decoded:
        raise AppError("登录已失效，请重新登录", code=401, http_status=401)
    admin_id = decoded["admin_id"]
    old_jti = decoded["jti"]
    stored_id = get_admin_refresh_admin_id(old_jti)
    if stored_id is None or stored_id != admin_id:
        raise AppError("登录已失效，请重新登录", code=401, http_status=401)
    # 先删旧：一次性使用
    delete_admin_refresh(old_jti)
    new_access = create_admin_access_token(admin_id)
    new_refresh, new_jti = create_admin_refresh_token(admin_id)
    # TTL：优先用新票寿命；也可用 settings 天数
    ttl = settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 3600
    store_admin_refresh(new_jti, admin_id, ttl)
    return AdminRefreshResult(token=new_access, refreshToken=new_refresh)


""" 退出登录 """


# 退出登录，传 access token 和 refresh token
# 拉黑 access token，作废 refresh token
def logout_admin(access_token: str, refresh_token: str | None = None) -> None:
    decoded = decode_admin_access_token(access_token)
    if not decoded:
        raise AppError("未登录或登录已过期", code=401, http_status=401)

    # 1) 拉黑 access token
    exp = decoded.get("exp")
    ttl = int(exp) - int(time.time()) if exp else 0
    blacklist_admin_access(decoded["jti"], ttl)

    # 2) 作废 refresh（有则删）
    if refresh_token:
        r = decode_admin_refresh_token(refresh_token)
        if r:
            delete_admin_refresh(r["jti"])
