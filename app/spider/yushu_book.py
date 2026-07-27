from app.libs.http_client import HTTP

from app.setting import DEFAULT_PAGE_SIZE
from app.secure import ISBN_KEY, YU_SHU_API_BASE

# 通过 secure 加载 .env + .env.{APP_ENV}
import app.secure  # noqa: F401

APP_KEY = ISBN_KEY


# 这里是根据关键字和ISBN搜索图书的类
class YuShuBook:
    isbn_url = (
        f"{YU_SHU_API_BASE}/sysAboutUs/findInfo?isbn={{isbn}}&appKey={{appKey}}"
    )
    keyword_url = (
        f"{YU_SHU_API_BASE}/sysAboutUs/findInfo"
        "?current={page}&size={size}&bookName={keyword}&appKey={appKey}"
    )

    # 初始化书籍信息
    def __init__(self):
        self.total = 0
        self.books = []

    # __是私有方法
    def __fill_single(self, data):
        if data:
            self.total = 1
            self.books.append(data)

    def __fill_collection(self, data):
        self.total = data["total"]
        self.books = data["records"]

    def search_by_isbn(self, isbn):
        url = self.isbn_url.format(isbn=isbn, appKey=APP_KEY)
        result = HTTP.get(url)
        self.__fill_single(result)

    def search_by_keyword(self, keyword, page=1, size=DEFAULT_PAGE_SIZE):
        url = self.keyword_url.format(
            keyword=keyword, page=page, size=size, appKey=APP_KEY
        )
        result = HTTP.get(url)
        self.__fill_collection(result)
