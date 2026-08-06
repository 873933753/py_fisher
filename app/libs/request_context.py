from contextvars import ContextVar

# 请求ID上下文变量
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


# 获取请求ID
def get_request_id() -> str | None:
    return request_id_ctx.get()


# 设置请求ID
def set_request_id(value: str):
    return request_id_ctx.set(value)


# 重置请求ID
def reset_request_id(token) -> None:
    request_id_ctx.reset(token)
