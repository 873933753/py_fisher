import re
from typing import Annotated, Optional

from pydantic import BaseModel, AfterValidator


def _validate_recipient_name(v: str) -> str:
    v = (v or "").strip()
    if not v:
        raise ValueError("收件人姓名不可以为空")
    if len(v) < 2 or len(v) > 20:
        raise ValueError("收件人姓名长度必须在2到20个字之间")
    return v


def _validate_mobile(v: str) -> str:
    v = (v or "").strip()
    if not v:
        raise ValueError("手机号不可以为空")
    if not re.fullmatch(r"^1[0-9]{10}$", v):
        raise ValueError("请输入正确的手机号")
    return v


def _validate_address(v: str) -> str:
    v = (v or "").strip()
    if not v:
        raise ValueError("邮寄地址不可以为空")
    if len(v) < 10 or len(v) > 70:
        raise ValueError("地址还不到10个字吗？尽量写详细一些")
    return v


def _validate_message(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = v.strip()
    if not v:
        return None  # 空字符串当未填
    if len(v) > 200:
        raise ValueError("留言最多200个字")
    return v


RecipientName = Annotated[str, AfterValidator(_validate_recipient_name)]
Mobile = Annotated[str, AfterValidator(_validate_mobile)]
Address = Annotated[str, AfterValidator(_validate_address)]
Message = Annotated[Optional[str], AfterValidator(_validate_message)]


class DriftForm(BaseModel):
    recipient_name: RecipientName
    mobile: Mobile
    message: Message = None
    address: Address
    gift_id: int
