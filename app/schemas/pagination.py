from typing import Annotated, Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlmodel import Session, select, func

from app.setting import DEFAULT_PAGE_SIZE, PAGE_SIZE_MIN, PAGE_SIZE_MAX

# ---------- 1) 路由查询参数（各接口复用）----------
Page = Annotated[int, Query(ge=1, le=999, description="页码，默认 1")]
PageSize = Annotated[
    int,
    Query(ge=PAGE_SIZE_MIN, le=PAGE_SIZE_MAX, description="每页条数"),
]

# ---------- 2) 通用分页响应壳 ----------
T = TypeVar("T")


class PageData(BaseModel, Generic[T]):
    page: int
    size: int
    total: int
    pages: int = 0
    items: List[T]

    @classmethod
    def build(cls, items: list[T], total: int, page: int, size: int) -> "PageData[T]":
        pages = (total + size - 1) // size if size else 0
        return cls(page=page, size=size, total=total, pages=pages, items=items)


# ---------- 3) SQL 分页工具 ----------
# 分页逻辑：先查询总条数，再查询本页数据
def paginate(session: Session, statement, page: int = 1, size: int = DEFAULT_PAGE_SIZE):
    """
    对任意 select(...) 做分页。
    返回: (本页数据列表, 总条数)
    """
    # 去掉 order_by 再 count，避免无意义排序影响 count
    # count_stmt: 查询总条数的语句
    # statement: 查询语句
    count_stmt = select(func.count()).select_from(statement.order_by(None).subquery())
    # total 总条数
    total = session.exec(count_stmt).one()
    # 在原查询基础上，添加 offset 和 limit
    items = session.exec(
        # 在原查询基础上，添加 offset 和 limit
        # statement.offset(offset).limit(limit) - 跳过 offset 条，取 limit 条
        statement.offset((page - 1) * size).limit(size)
    ).all()
    return items, total
