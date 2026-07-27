import re  # 正则表达式
from typing import Annotated
from pydantic import (
    BaseModel,
    field_validator,
    AfterValidator,
    ValidationInfo,
)


# 邮箱验证规则
def _strip_required_email(v: str) -> str:
    v = (v or "").strip()
    if not v:
        # ValueError 是 Python 内置的异常类型，表示值错误或异常
        # 422
        raise ValueError("请输入正确的邮箱")
    return v


def _validate_register_email(v: str) -> str:
    v = _strip_required_email(
        v
    )  # 先复用基础规则；若文案要「电子邮箱不可以为空」可单独写
    if len(v) < 8 or len(v) > 64:
        raise ValueError("电子邮箱长度需在8到64个字符之间")
    if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
        raise ValueError("电子邮箱不符合规范")
    return v


# 昵称验证规则
def _validate_nickname(v: str) -> str:
    v = (v or "").strip()
    if not v:
        raise ValueError("昵称不可以为空")
    if len(v) < 2 or len(v) > 10:
        raise ValueError("昵称至少需要两个字符，最多10个字符")
    return v


# 密码验证规则
def _validate_password(v: str) -> str:
    v = (v or "").strip()
    if not v:
        raise ValueError("密码不可以为空，请输入你的密码")
    if len(v) < 6 or len(v) > 32:
        raise ValueError("密码长度需在6到32个字符之间")
    return v


# 昵称类型 - 使用注解
Nickname = Annotated[
    str,
    # StringConstraints - 字符串约束
    # strip_whitespace=True - 去空格
    # min_length=2 - 最小长度2
    # max_length=10 - 最大长度10
    # 这里如果用StringConstraints走的是 Pydantic 内置校验，返回的是英文提示
    # StringConstraints(strip_whitespace=True, min_length=2, max_length=10),
    # 这里如果用AfterValidator走的是自定义校验，返回的是中文提示
    AfterValidator(_validate_nickname),
]

# 登录 / 找回密码等：只要求有邮箱
Email = Annotated[str, AfterValidator(_validate_register_email)]

# 注册：完整校验
RegisterEmail = Annotated[str, AfterValidator(_validate_register_email)]

# 密码类型 - 使用注解
Password = Annotated[str, AfterValidator(_validate_password)]


class RegisterForm(BaseModel):
    email: Email
    password: Password
    nickname: Nickname


class LoginForm(BaseModel):
    email: Email
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("密码不可以为空，请输入你的密码")
        return v


class EmailForm(BaseModel):
    email: Email


class ResetPasswordForm(BaseModel):
    new_password: Password
    confirm_password: Password

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: ValidationInfo) -> str:
        password = (info.data or {}).get("new_password")
        if password is not None and v != password:
            raise ValueError("两次密码不一致")
        return v


class VerifyCodeForm(BaseModel):
    email: Email
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("验证码不可以为空")
        if len(v) != 6:
            raise ValueError("验证码长度为6位")
        return v


class ResetPasswordTokenForm(BaseModel):
    reset_token: str
    new_password: Password
    confirm_password: Password

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: ValidationInfo) -> str:
        password = (info.data or {}).get("new_password")
        if password is not None and v != password:
            raise ValueError("两次密码不一致")
        return v
