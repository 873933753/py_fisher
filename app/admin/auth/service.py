from sqlmodel import Session, select

from app.admin.auth.schemas import AdminInfo, AdminLoginIn, AdminLoginResult
from app.admin.models import AdminUser
from app.admin.security import create_admin_access_token
from app.libs.exceptions import AppError
from app.libs.security import verify_password


# 登录业务逻辑
def login_admin(session: Session, body: AdminLoginIn) -> AdminLoginResult:
    admin = session.exec(
        select(AdminUser).where(AdminUser.phone_number == body.phone_number)
    ).first()

    # 账号不存在与密码错误同一文案，降低枚举风险
    if not admin or not verify_password(body.password, admin.password_hash):
        raise AppError("手机号或密码错误")

    token = create_admin_access_token(admin.id)

    info = AdminInfo(id=admin.id, phone_number=admin.phone_number, role=admin.role)
    return AdminLoginResult(
        token=token,
        userInfo=info,
    )
