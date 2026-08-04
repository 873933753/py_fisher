import re  # 正则表达式
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


# 响应包装 - 通用响应包装
class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: Optional[T] = None


# 登录请求
class AdminLoginIn(BaseModel):
    phone_number: str = Field(min_length=1, max_length=18)
    password: str = Field(min_length=6, max_length=64)
    # phone_number: str
    # password: str

    # 验证手机号
    # 使用 field_validator 装饰器，验证手机号是否符合正则表达式
    # 使用 @classmethod 装饰器，使方法成为类方法，需要传递 cls 参数,可调用类属性
    # staticmethod 装饰器，使方法成为静态方法
    # 静态方法不需要传递 self 参数
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("请输入手机号")
        if not re.fullmatch(r"1[3-9]\d{9}", v):
            raise ValueError("手机号格式错误")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("请输入密码")
        if len(v) > 64:
            raise ValueError("密码长度不能超过64个字符")
        return v


# 后台用户信息，登录和获取用户信息时使用
class AdminInfo(BaseModel):
    id: int
    phone_number: str
    role: str
    # 从数据库中获取数据时，自动将数据库中的数据转换为模型中的数据
    model_config = {"from_attributes": True}


class AdminLoginResult(BaseModel):
    token: str
    userInfo: AdminInfo
