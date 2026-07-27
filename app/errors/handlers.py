from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.libs.exceptions import AppError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from starlette.exceptions import HTTPException as StarletteHTTPException


def register_exception_handlers(app: FastAPI) -> None:
    # 应用错误处理 - 自定义异常
    @app.exception_handler(AppError)
    async def app_error_handler(request, exc: AppError):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": None,
            },
        )

    # 参数校验失败处理
    # RequestValidationError 是 FastAPI 内置的异常类，用于处理请求参数校验失败的情况
    # 当请求参数校验失败时，会抛出 RequestValidationError 异常
    # 使用的地方：app/forms/auth.py
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": _first_validation_message(exc),
                "data": None,
            },
        )

    # 数据库写入失败处理
    # IntegrityError 是 SQLAlchemy 内置的异常类，用于处理数据库写入失败的情况
    # 当数据库写入失败时，会抛出 IntegrityError 异常
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        # 可在这里 log.exception(exc)
        return JSONResponse(
            status_code=400,  # 或 409，看你语义
            content={
                "code": 400,
                "message": "数据写入失败，请稍后重试",
                "data": None,
            },
        )

    # SQLAlchemyError 是 SQLAlchemy 内置的异常类，用于处理数据库查询失败的情况
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        # 记录异常日志
        logging.exception(exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务繁忙，请稍后重试",
                "data": None,
            },
        )

    # 处理HTTP异常，比如404
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # 可按 status_code 细分文案 / 业务码
        message = "接口不存在" if exc.status_code == 404 else (exc.detail or "请求失败")
        code = exc.status_code
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": code,
                "message": message,
                "data": None,
            },
        )


# 获取第一个参数校验失败的消息
# 只取第一条错误,多个字段同时出错时，只返回第一个 message。对注册表单通常够用
# 私有方法 - 只用于内部使用
def _first_validation_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "参数校验失败"

    err = errors[0]

    # 字段缺失 → 统一中文
    # if err.get("type") == "missing":
    #     return "参数缺失"

    err_type = err.get("type")
    loc = err.get("loc", [])
    field = loc[-1] if loc else "参数"
    if err_type == "missing":
        return f"{field} 不能为空"
    if err_type in ("int_parsing", "int_type"):
        return f"{field} 必须是整数"
    if err_type == "greater_than":
        return f"{field} 必须大于 {err.get('ctx', {}).get('gt')}"

    msg = err.get("msg", "参数校验失败")
    if msg.startswith("Value error, "):
        msg = msg[len("Value error, ") :]
    return msg
