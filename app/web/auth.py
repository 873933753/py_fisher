# 登录注册模块
from . import web_router
from app.forms.auth import RegisterForm, LoginForm
from app.schemas.response import ApiResponse
from app.models.user import User
from sqlmodel import Session
from app.database import get_session, auto_commit
from fastapi import Depends, Request, Form, BackgroundTasks
from app.libs.security import hash_password, verify_password
from app.libs.exceptions import AppError
from sqlmodel import select
from app.schemas.user import UserInfo, LoginResult

# 导入生成访问令牌和登录结果模型
from app.libs.security import create_access_token
from app.libs.auth import get_current_user
from app.forms.auth import (
    EmailForm,
    ResetPasswordForm,
    VerifyCodeForm,
    ResetPasswordTokenForm,
)
from app.libs.security import create_reset_token, decode_reset_token
from app.setting import RESET_PASSWORD_CODE_TTL, RESET_PASSWORD_SEND_COOLDOWN


""" 
客户端 POST /register
    ↓
FastAPI 用 RegisterForm 解析请求体  
    ↓
校验失败 → 抛 RequestValidationError → handlers.py 返回 422
    ↓
校验成功 → 才执行 register(form)
"""


# 注册接口
# response_model - 响应模型，返回用户信息
@web_router.post("/register", response_model=ApiResponse[UserInfo])
def register(form: RegisterForm, session: Session = Depends(get_session)):
    # 检查邮箱是否已注册
    existing = session.exec(select(User).where(User.email == form.email)).first()
    if existing:
        raise AppError("电子邮箱已被注册")

    # 进入到这里,说明表单验证通过
    # 这里可以进行数据库操作
    data = form.model_dump()
    # 移除password字段 - 防止密码明文存储在数据库中
    plain = data.pop("password")  # 拿走明文
    user = User()
    # 只set其他属性，不set password_hash属性
    user.set_attrs(data)
    user.password_hash = hash_password(plain)
    # 写入数据库
    with auto_commit(session):
        session.add(user)  # 添加到数据库

    # 注册成功 - 返回用户信息
    user_info = UserInfo.model_validate(user)
    return ApiResponse(data=user_info, message="注册成功")


# 登录接口
@web_router.post("/login", response_model=ApiResponse[LoginResult])
def login(form: LoginForm, session: Session = Depends(get_session)):
    # 检查邮箱密码是否匹配
    """
    1)按邮箱查用户
    2)校验查出来的用户密码是否匹配
    """
    # 1)按邮箱查用户
    user = session.exec(select(User).where(User.email == form.email)).first()

    # 2)校验查出来的用户密码是否匹配
    # “用户不存在”和“密码错误”应返回同一条消息（如 "邮箱或密码错误"），降低邮箱枚举风险
    if not user or not verify_password(form.password, user.password_hash):
        raise AppError("邮箱或密码错误")

    # 邮箱密码匹配 - 登录成功并返回用户信息
    user_info = UserInfo.model_validate(user)

    # 生成访问令牌
    token = create_access_token(user.id)
    return ApiResponse(
        data=LoginResult(token=token, user=user_info), message="登录成功"
    )


# 验证JWT token的接口
# 使用get_current_user装饰器获取当前用户，返回用户信息，给前端展示用户信息
@web_router.get("/profile", response_model=ApiResponse[UserInfo])
def profile(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserInfo.model_validate(current_user))


# 忘记密码 - 发送重置密码邮件
@web_router.post("/forgetPassword", response_model=ApiResponse[dict])
def forgetPassword(
    form: EmailForm,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = User.get_user_by_email(session, form.email)
    if not user:
        raise AppError("邮箱不存在")

    from app.libs.email import send_email_safe

    # 邮箱存在，后台发送重置密码邮件
    reset_url = f"http://127.0.0.1:8000/web/reset/password/{user.generate_token()}"

    background_tasks.add_task(
        send_email_safe,
        # to=form.email,
        to="tang_tk001@outlook.comxxx",
        subject="重置你的密码",
        template="email/reset_password.html",
        user={"email": "亲爱的用户"},
        reset_url=reset_url,
    )
    return ApiResponse(
        data={"reset_url": reset_url}, message="已提交发送重置邮件，请查收邮箱"
    )


# 重置密码页面
@web_router.get("/reset/password/{token}")
def reset_password_page(token: str, request: Request):
    from app.libs.templates import templates

    return templates.TemplateResponse(
        request=request,
        name="auth/forget_password.html",
        context={"request": request, "token": token},
    )


# post请求，重置密码
# Form接参 + Pydantic 校验
@web_router.post("/reset/password/{token}", response_model=ApiResponse[dict])
def reset_password(
    token: str,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    session: Session = Depends(get_session),
):
    # 导入ValidationError-用于处理表单验证错误
    from pydantic import ValidationError
    from fastapi.exceptions import RequestValidationError

    try:
        # 这里才会走 ResetPasswordForm 的长度/两次一致等规则
        # 失败 → RequestValidationError → 你们 handlers 返回 422 JSON
        form = ResetPasswordForm(
            new_password=new_password,
            confirm_password=confirm_password,
        )
    except ValidationError as e:
        raise RequestValidationError(e.errors())

    # 2、验证token是否有效
    user = User.validate_token(session, token)

    # 3、重置密码
    user.reset_password(form.new_password, session)

    return ApiResponse(data={}, message="密码重置成功")


# 忘记密码 - 发送邮箱验证码================================================
@web_router.post("/forgetPassword/sendCode", response_model=ApiResponse[dict])
def forgetPassword_sendCode(
    form: EmailForm,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = User.get_user_by_email(session, form.email)
    if not user:
        raise AppError("邮箱不存在")

    from app.libs.email import send_email_safe
    from app.libs.helper import generate_verify_code
    from app.libs.redis import (
        redis_client,
        reset_password_code_key,
        reset_password_send_limit_key,
    )

    # 限流：60 秒内同一邮箱只能发一次
    allowed = redis_client.set(
        reset_password_send_limit_key(form.email),
        "1",
        nx=True,
        ex=RESET_PASSWORD_SEND_COOLDOWN,
    )
    if not allowed:  # 写入，已存在返回None，不存在返回True
        raise AppError("发送过于频繁，请稍后再试", code=429, http_status=429)

    # 通过限流后，再生成验证码、存 Redis、发邮件
    # 邮箱存在，后台发送重置密码邮件
    code = generate_verify_code()
    # 将验证码存入redis
    redis_client.set(reset_password_code_key(user.id), code, ex=RESET_PASSWORD_CODE_TTL)

    background_tasks.add_task(
        send_email_safe,
        to=form.email,
        # to='tang_tk001@outlook.comxxx',
        subject="重置你的密码",
        template="email/reset_password_code.html",
        user={"email": form.email},
        code=code,
    )
    return ApiResponse(
        data={
            # "code": code
        },
        message="验证码已发送，请查收邮箱",
    )


# 验证验证码，返回reset_token
@web_router.post("/forgetPassword/verifyCode", response_model=ApiResponse[dict])
def forgetPassword_verifyCode(
    form: VerifyCodeForm, session: Session = Depends(get_session)
):
    user = User.get_user_by_email(session, form.email)
    if not user:
        raise AppError("邮箱不存在")

    from app.libs.redis import redis_client
    from app.libs.redis import reset_password_code_key

    # 校验验证码
    stored_code = redis_client.get(reset_password_code_key(user.id))

    if not stored_code or stored_code != form.code:
        raise AppError("验证码错误")

    # 删除验证码
    redis_client.delete(reset_password_code_key(user.id))

    # 返回reset_token
    # reset_token = user.generate_token()

    # 创建reset_token并存入redis
    reset_token, jti = create_reset_token(user.id, expiration=600)
    redis_client.set(
        f"reset_password_jti:{jti}",
        user.id,
        ex=RESET_PASSWORD_CODE_TTL,  # 与 token 过期时间一致
    )

    return ApiResponse(
        data={
            # 测试用
            "reset_token": reset_token,
            # "jti": f"reset_password_jti:{jti}"
        },
        message="验证码验证成功",
    )


# 校验凭证+重置密码
@web_router.post("/forgetPassword/resetPassword", response_model=ApiResponse[dict])
def forgetPassword_resetPassword(
    form: ResetPasswordTokenForm, session: Session = Depends(get_session)
):
    from app.libs.redis import redis_client

    result = decode_reset_token(form.reset_token)
    if not result:
        raise AppError("凭证无效或已过期")

    user_id, jti = result
    # 删除redis中的user_id的key
    # 从redis中获取user_id
    key = f"reset_password_jti:{jti}"
    # GET + DEL 原子操作，防止并发重复提交
    stored_user_id = redis_client.getdel(key)
    if not stored_user_id or int(stored_user_id) != user_id:
        raise AppError("凭证无效或已过期")

    # 重置密码
    user = session.get(User, user_id)
    user.reset_password(form.new_password, session)

    # 删除reset_token
    return ApiResponse(data={}, message="密码重置成功")
