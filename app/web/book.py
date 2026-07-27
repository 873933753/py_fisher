from app.libs.helper import is_isbn_or_key
from app.spider.yushu_book import YuShuBook
from . import web_router
from typing import Annotated
from pydantic import StringConstraints
from fastapi import Query
from app.setting import DEFAULT_PAGE_SIZE, PAGE_SIZE_MIN, PAGE_SIZE_MAX
from app.view_models.book import BookCollectionViewModel

# 搜索关键字或 ISBN
SearchQuery = Annotated[
    str,
    # strip_whitespace=True 会先去掉前后空格，再做长度校验。
    # min_length / max_length 放在 StringConstraints 里，不要同时写在 Query() 里，避免先校验长度、后去空格导致 " 活着 " 这类输入误判
    StringConstraints(strip_whitespace=True, min_length=1, max_length=30),
    # Query 是 FastAPI 的查询参数验证器
    # ... 表示q必填参数
    # min_length 和 max_length 是字符串长度验证
    Query(..., description="搜索关键字或 ISBN"),
]

# 页码
# 默认值为1,最小值为1,最大值为999
# ge 和 le 是数字范围验证
Page = Annotated[int, Query(ge=1, le=999, description="页码，默认 1")]

PageSize = Annotated[
    int, Query(ge=PAGE_SIZE_MIN, le=PAGE_SIZE_MAX, description="每页条数")
]


@web_router.get("/book/search")
def search(
    q: SearchQuery,
    page: Page = 1,
    size: PageSize = DEFAULT_PAGE_SIZE,
):
    """
    ISBN搜索接口：https://data.isbn.work/openApi/getInfoByIsbn?isbn=9787115611833&appKey=
    关键字搜索接口：https://data.isbn.work/openApi/book/page?current=1&size=10&bookName=活着&appKey
    q - 关键字和ISBN
    page - 页码
    """
    # 包装书籍信息
    books = BookCollectionViewModel()
    isbn_or_key = is_isbn_or_key(q)
    yushu_book = YuShuBook()

    if isbn_or_key == "isbn":
        # result = YuShuBook.search_by_isbn(q)
        yushu_book.search_by_isbn(q)
    else:
        # result = YuShuBook.search_by_keyword(q, page, size)
        yushu_book.search_by_keyword(q, page, size)

    books.fill(yushu_book, q)
    return books
