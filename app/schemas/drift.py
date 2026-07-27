from typing import List
from pydantic import BaseModel
from app.libs.enums import DriftStatus
from app.libs.helper import FormattedDateTime


class DriftItem(BaseModel):
    id: int
    recipient_name: str
    message: str | None = None
    product_title: str
    isbn: str
    product_img: str
    status: DriftStatus
    create_time: FormattedDateTime
    gifter_nickname: str
    requester_nickname: str
    gifter_id: int
    requester_id: int
    gift_id: int
    you_are: str
    status_str: str
    operator: str
    address: str
    mobile: str


# drift -detail
class DriftDetail(DriftItem):
    mobile: str
    address: str


class DriftListData(BaseModel):
    items: List[DriftItem]
