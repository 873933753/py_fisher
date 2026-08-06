import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.libs.request_context import reset_request_id, set_request_id

# 请求ID头名称
HEADER_NAME = "X-Request-ID"


# 请求ID中间件
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # 允许上游（网关）传入；没有则本地生成
        rid = request.headers.get(HEADER_NAME) or uuid.uuid4().hex
        # 设置requestId
        ctx_token = set_request_id(rid)
        try:
            response = await call_next(request)
            # 设置日志看格式是否生效
            # import logging

            # logger = logging.getLogger(__name__)

            # logger.info(
            #     "request done method=%s path=%s status=%s",
            #     request.method,
            #     request.url.path,
            #     response.status_code,
            # )
            response.headers[HEADER_NAME] = rid
            return response
        finally:
            # finally 里 reset，避免污染后续请求
            reset_request_id(ctx_token)
