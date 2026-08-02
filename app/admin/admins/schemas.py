import re
from typing import Optional

from pydantic import BaseModel, Field, computed_field, field_validator

from app.libs.helper import FormattedDateTime


class DisabledFromDeletedMixin(BaseModel):
    is_deleted: int = Field(exclude=True)

    @computed_field
    @property
    def is_disabled(self) -> bool:
        return self.is_deleted != 0


class AdminAccountItem(DisabledFromDeletedMixin):
    """后台账号列表/详情"""

    id: int
    phone_number: str
    create_time: FormattedDateTime
    role: str

    model_config = {"from_attributes": True}


class AdminAccountCreateIn(BaseModel):
    phone_number: str = Field(min_length=1, max_length=18)
    password: str = Field(min_length=6, max_length=64)

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
        if len(v) < 6:
            raise ValueError("密码至少6位")
        return v


class AdminAccountUpdateIn(BaseModel):
    """全可选；有 password 才重置密码。"""

    phone_number: Optional[str] = Field(default=None, max_length=18)
    password: Optional[str] = Field(default=None, min_length=6, max_length=64)
    is_disabled: bool | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("请输入手机号")
        if not re.fullmatch(r"1[3-9]\d{9}", v):
            raise ValueError("手机号格式错误")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 6:
            raise ValueError("密码至少6位")
        return v
