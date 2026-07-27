# 辅助函数
from datetime import datetime, timezone, timedelta
from typing import Annotated, Any

from pydantic import BeforeValidator

CN_TZ = timezone(timedelta(hours=8))
TIME_FMT = "%Y-%m-%d %H:%M:%S"


def is_isbn_or_key(keyword):
    # isbn isbn13 13个0-9的数字组成
    # isbn10 10个0-9的数字组成，包含-符号

    is_isbn = "key"
    # ISBN的判断
    if len(keyword) == 13 and keyword.isdigit():
        is_isbn = "isbn"
    short_q = keyword.replace("-", "")
    if "-" in keyword and len(short_q) == 10 and short_q.isdigit():
        is_isbn = "isbn"
    return is_isbn


def format_datetime(v: Any) -> Any:
    """把 int 时间戳 / datetime 转成东八区可读字符串。"""
    if isinstance(v, int):
        return datetime.fromtimestamp(v, tz=CN_TZ).strftime(TIME_FMT)
    if isinstance(v, datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(CN_TZ).strftime(TIME_FMT)
    return v


# 用于 Pydantic 字段：传入 int/datetime，输出格式化字符串
FormattedDateTime = Annotated[str, BeforeValidator(format_datetime)]

import random
import string


# 生成验证码，默认6位，纯数字
def generate_verify_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))
