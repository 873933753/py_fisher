from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field

from app.admin.base import AdminBaseModel


# table=True 表示将模型映射到数据库表
class AdminUser(AdminBaseModel, table=True):
    """后台管理员账号（与前台 user 表独立）。"""

    __tablename__ = "admin_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    # 登录账号：手机号，唯一
    phone_number: str = Field(max_length=18, unique=True, index=True)
    # 模型字段 password_hash；库列名 password（与前台 User 一致）
    password_hash: str = Field(
        sa_column=Column("password", String(256), nullable=False)
    )
