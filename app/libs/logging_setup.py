import logging
import sys

from app.libs.request_context import get_request_id


# 请求ID过滤器，根据request_id过滤日志
class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


# Formatter 格式化日志
def setup_logging(level: str = "INFO") -> None:
    """进程启动时调用一次。"""
    root = logging.getLogger()
    if getattr(root, "_hanber_logging_configured", False):
        return

    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level.upper())
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s [request_id=%(request_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # 避免重复 addHandler（reload 时）
    root.handlers.clear()
    root.addHandler(handler)

    # 替代 SQL_ECHO：sqlalchemy 命名空间默认 WARNING，需显式打开
    # 开发(DEBUG)打 SQL；生产(INFO)保持安静。保持 create_engine(echo=False)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if level.upper() == "DEBUG" else logging.WARNING
    )

    root._hanber_logging_configured = True  # type: ignore[attr-defined]
