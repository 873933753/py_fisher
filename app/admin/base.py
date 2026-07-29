from datetime import datetime

from sqlmodel import Field, SQLModel

from app.admin.soft_delete import SoftDeleteMixin


# 顺序与前台一致：SQLModel 在前，Mixin 在后
class AdminBaseModel(SQLModel, SoftDeleteMixin):
    create_time: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
