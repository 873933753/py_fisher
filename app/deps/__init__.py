from app.deps.common import CurrentSession, CurrentUser
from app.deps.resources import (
    get_waiting_drift_as_requester,
    get_waiting_drift_as_gifter,
    get_mailable_drift_as_gifter,
    get_requestable_gift_from_query,
    get_requestable_gift_from_drift_form,
    can_send_dependency,
)
from app.deps.gift_resource import get_own_active_gift_from_path
from app.deps.wish_resource import get_own_active_wish_from_path

# 导出公共依赖
__all__ = [
    "CurrentSession",
    "CurrentUser",
    "get_waiting_drift_as_requester",
    "get_waiting_drift_as_gifter",
    "get_mailable_drift_as_gifter",
    "get_requestable_gift_from_query",
    "get_requestable_gift_from_drift_form",
    "can_send_dependency",
    # gift_resource
    "get_own_active_gift_from_path",
    # wish_resource
    "get_own_active_wish_from_path",
]
