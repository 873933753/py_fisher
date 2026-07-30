from typing import Annotated, Any, Optional

from pydantic import BaseModel, BeforeValidator, Field, computed_field

from app.libs.helper import FormattedDateTime  # 基础设施，可复用


# 用于 Pydantic 字段：传入 None，输出空字符串
def none_to_empty(v: Any) -> str:
    return "" if v is None else v


EmptyStr = Annotated[str, BeforeValidator(none_to_empty)]


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
    nickname: EmptyStr = ""
    avatar: EmptyStr = ""
    beans: int
    create_time: FormattedDateTime
    update_time: FormattedDateTime | EmptyStr = ""
    # is_deleted: int
    # 开启后，FrontUserItem.model_validate(obj) 会按 属性名 从 obj 上读取字段
    model_config = {"from_attributes": True}


# 详情 - 在列表字段上扩展
class FrontUserDetail(FrontUserItem):
    """详情（在列表字段上扩展）。"""

    phone_number: EmptyStr = ""
    send_counter: int
    receive_counter: int
    wx_open_id: EmptyStr = ""
    wx_name: EmptyStr = ""


class FrontUserUpdateIn(BaseModel):
    """PATCH 白名单；全可选，只更新传入的字段。"""

    nickname: Optional[str] = Field(default=None, max_length=24)
    avatar: Optional[str] = Field(default=None, max_length=255)
    beans: Optional[int] = Field(default=None, ge=0)
    phone_number: Optional[str] = Field(default=None, max_length=18)
    is_disabled: bool | None = None  # 前端布尔；不要 is_deleted
