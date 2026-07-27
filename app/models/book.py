# app/models/book.py
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseModel


# 书籍模型
class Book(BaseModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True
    )  # 主键，自动递增，primary_key=True不会重复
    title: str = Field(max_length=50)  # 标题，最大长度50
    author: str = Field(default="未名", max_length=30)  # 作者，最大长度30
    binding: Optional[str] = Field(default=None, max_length=20)  # 装订，最大长度20
    publisher: Optional[str] = Field(default=None, max_length=50)  # 出版社，最大长度50
    price: Optional[str] = Field(default=None, max_length=20)  # 价格，最大长度20
    pages: Optional[int] = None  # 页数，None表示不限制
    pubdate: Optional[str] = Field(default=None, max_length=20)  # 出版日期，最大长度20
    isbn: str = Field(
        max_length=15, unique=True, index=True
    )  # ISBN，最大长度15，唯一，index=True索引
    summary: Optional[str] = Field(default=None, max_length=1000)  # 摘要，最大长度1000
    image: Optional[str] = Field(default=None, max_length=50)  # 图片，最大长度50
