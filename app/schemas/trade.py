from pydantic import BaseModel

from app.libs.helper import FormattedDateTime


class TradeItem(BaseModel):
    id: int
    time: FormattedDateTime
    user_id: int | None = None
    email: str | None = None


# class TradeListData(BaseModel):
#     total: int
#     trades: list[TradeItem]


class TradeListData(BaseModel):
    total: int
    trades: list[TradeItem]
    user_type: int | None = None  # 0 无 / 1 赠送者 / 2 索要者；列表接口可不传
