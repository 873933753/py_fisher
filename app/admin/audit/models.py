from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class AdminOperationLog(SQLModel, table=True):
    """管理端操作审计日志：只追加，不软删。"""

    __tablename__ = "admin_operation_log"

    id: Optional[int] = Field(default=None, primary_key=True)

    operator_id: Optional[int] = Field(default=None, index=True)
    operator_name: Optional[str] = Field(default=None, max_length=64)
    operator_role: Optional[str] = Field(default=None, max_length=32, index=True)

    module: str = Field(max_length=32, index=True)  # users / admins
    action: str = Field(max_length=32, index=True)  # create / update / delete
    resource_type: Optional[str] = Field(default=None, max_length=32)
    resource_id: Optional[str] = Field(default=None, max_length=64, index=True)

    method: Optional[str] = Field(default=None, max_length=16)
    path: Optional[str] = Field(default=None, max_length=255)
    ip: Optional[str] = Field(default=None, max_length=64)
    user_agent: Optional[str] = Field(default=None, max_length=512)

    # 长文本用 Text，避免 VARCHAR 过短截断业务摘要
    request_summary: Optional[str] = Field(default=None, sa_column=Column(Text))
    before_summary: Optional[str] = Field(default=None, sa_column=Column(Text))
    after_summary: Optional[str] = Field(default=None, sa_column=Column(Text))

    success: bool = Field(default=True, index=True)
    error_message: Optional[str] = Field(default=None, max_length=512)

    create_time: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        index=True,
    )
