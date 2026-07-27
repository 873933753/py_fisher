class AppError(Exception):
    """应用业务异常基类，全局 handler 统一处理其子类"""

    def __init__(self, message: str, code: int = 400, http_status: int = 400):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)


class SpiderError(AppError):
    """第三方爬虫/接口请求失败时抛出"""

    def __init__(self, message: str):
        super().__init__(message, code=502, http_status=502)
