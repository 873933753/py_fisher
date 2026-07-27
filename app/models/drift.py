from typing import Optional
from sqlmodel import Field
from app.models.base import BaseModel
from app.libs.enums import DriftStatus
from sqlalchemy import Column, Integer
from sqlmodel import select


class Drift(BaseModel, table=True):
    """一次具体的交易信息"""

    id: Optional[int] = Field(default=None, primary_key=True)

    # 邮寄信息
    recipient_name: str = Field(max_length=20)
    address: str = Field(max_length=100)
    message: Optional[str] = Field(default=None, max_length=200)
    mobile: str = Field(max_length=20)

    # 书籍信息
    isbn: Optional[str] = Field(default=None, max_length=50)
    product_title: Optional[str] = Field(default=None, max_length=50)
    book_author: Optional[str] = Field(default=None, max_length=30)
    product_img: Optional[str] = Field(default=None, max_length=255)

    # 请求者信息
    requester_id: Optional[int] = None
    requester_nickname: Optional[str] = Field(default=None, max_length=20)

    # 赠送者信息
    gifter_id: Optional[int] = None
    gift_id: Optional[int] = None
    gifter_nickname: Optional[str] = Field(default=None, max_length=20)

    # 交易状态
    status: DriftStatus = Field(
        default=DriftStatus.Waiting,
        sa_column=Column(Integer, nullable=False, default=1),
    )

    # 查当前用户的交易列表
    @classmethod
    def get_drift_list(cls, user_id: int):
        # 这里只返回查询对象，不执行查询，由分页执行
        return (
            select(cls)
            .where((cls.requester_id == user_id) | (cls.gifter_id == user_id))
            .order_by(cls.create_time.desc())
        )
