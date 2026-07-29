from typing import Optional

from pydantic import BaseModel, Field, computed_field

from app.libs.helper import FormattedDateTime  # 基础设施，可复用


class DisabledFromDeletedMixin(BaseModel):
    """从 User 灌进来，但不出现在 JSON 里"""

    is_deleted: int = Field(exclude=True)

    # 计算属性
    @computed_field
    @property
    def is_disabled(self) -> bool:
        return self.is_deleted != 0


# 列表项 - 在基类上扩展
class FrontUserItem(DisabledFromDeletedMixin):
    """列表项（精简）。"""

    id: int
    email: str
    nickname: Optional[str] = None
    beans: int
    create_time: FormattedDateTime
    # is_deleted: int
    # 开启后，FrontUserItem.model_validate(obj) 会按 属性名 从 obj 上读取字段
    model_config = {"from_attributes": True}


# 详情 - 在列表字段上扩展
class FrontUserDetail(FrontUserItem):
    """详情（在列表字段上扩展）。"""

    phone_number: Optional[str] = None
    send_counter: int
    receive_counter: int
    wx_open_id: Optional[str] = None
    wx_name: Optional[str] = None


class FrontUserUpdateIn(BaseModel):
    """PATCH 白名单；全可选，只更新传入的字段。"""

    nickname: Optional[str] = Field(default=None, max_length=24)
    beans: Optional[int] = Field(default=None, ge=0)
    phone_number: Optional[str] = Field(default=None, max_length=18)
    is_disabled: bool | None = None  # 前端布尔；不要 is_deleted
