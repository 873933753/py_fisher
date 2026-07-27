from app.libs.http_client import HTTP, HttpResult
from app.libs.exceptions import SpiderError

from app.setting import DEFAULT_PAGE_SIZE
from app.secure import ISBN_KEY, YU_SHU_API_BASE

# 通过 secure 加载 .env + .env.{APP_ENV}
import app.secure  # noqa: F401

APP_KEY = ISBN_KEY


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class YuShuProduct:
    isbn_url = (
        f"{YU_SHU_API_BASE}/product/queryByDictPage"
        "?current={page}&size={size}&bookName={keyword}&appKey={appKey}"
    )
    keyword_url = (
        f"{YU_SHU_API_BASE}/product/queryByDictPage"
        "?current={page}&size={size}&bookName={keyword}&appKey={appKey}"
    )

    def __init__(self):
        self.total = 0
        self.pages = 0
        self.list = []
        self.type = ""

    def __handle_result(self, result: HttpResult):
        if not result.ok:
            raise SpiderError(result.message or "第三方接口请求失败")

        body = result.data
        if not isinstance(body, dict):
            raise SpiderError("第三方返回数据格式异常")

        return body

    def __fill_single(self, body):
        self.type = "single"
        item = body.get("data") if isinstance(body.get("data"), dict) else body
        if item:
            self.total = 1
            self.pages = 1
            self.list = [item]

    def __fill_collection(self, body):
        # 第三方结构: {"code": 200, "data": {"records": [], "total": "15", "pages": "2", ...}}
        page_data = body.get("data") or body

        self.total = _to_int(page_data.get("total"))
        self.pages = _to_int(page_data.get("pages"))
        self.list = page_data.get("records") or []
        self.type = "list"

    def search_by_isbn(self, isbn):
        url = self.isbn_url.format(isbn=isbn, appKey=APP_KEY)
        result = HTTP.get(url)
        body = self.__handle_result(result)
        self.__fill_single(body)

    def search_by_keyword(self, keyword, page=1, size=DEFAULT_PAGE_SIZE):
        url = self.keyword_url.format(
            keyword=keyword, page=page, size=size, appKey=APP_KEY
        )
        result = HTTP.post(
            url,
            json={
                "productName": keyword,
                "dictIds": "",
                "current": page,
                "size": size,
            },
        )
        body = self.__handle_result(result)
        self.__fill_collection(body)

    # 获取第一条数据 - 详情
    # property装饰器 - 将方法转换为属性
    @property
    def first(self):
        return self.list[0] if self.total > 0 else None
