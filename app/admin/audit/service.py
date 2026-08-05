import json
from typing import Any

from sqlmodel import Session, col, select

from app.admin.audit.models import AdminOperationLog
from app.admin.audit.schemas import OperationLogDetail, OperationLogListItem
from app.admin.models import AdminUser
from app.database import auto_commit
from app.libs.exceptions import AppError
from app.schemas.pagination import PageData, paginate
from app.setting import DEFAULT_PAGE_SIZE

# 需要脱敏的字段
# 摘要里出现这些 key 时替换为 ***，避免敏感信息泄露
_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "token",
        "refreshToken",
        "refresh_token",
        "access_token",
    }
)


def _mask(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: ("***" if k in _SENSITIVE_KEYS else _mask(v)) for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_mask(x) for x in obj]
    return obj


def _to_summary(data: Any | None) -> str | None:
    if data is None:
        return None
    if isinstance(data, str):
        return data[:4000]
    return json.dumps(_mask(data), ensure_ascii=False, default=str)[:4000]


# 写入操作日志
def write_audit(
    session: Session,
    *,
    operator: AdminUser | None,
    module: str,
    action: str,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    method: str | None = None,
    path: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    request_summary: Any | None = None,
    before_summary: Any | None = None,
    after_summary: Any | None = None,
    success: bool = True,
    error_message: str | None = None,
    use_own_commit: bool = True,
) -> None:
    """
    写入一条操作日志。
    use_own_commit=True：独立 auto_commit（推荐先这样，业务已 commit 后再记审计）。
    use_own_commit=False：只 session.add，由外层事务一起提交。
    """
    log = AdminOperationLog(
        operator_id=operator.id if operator else None,
        operator_name=operator.phone_number if operator else None,
        operator_role=operator.role if operator else None,
        module=module,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        method=method,
        path=path,
        ip=ip,
        user_agent=(user_agent[:512] if user_agent else None),
        request_summary=_to_summary(request_summary),
        before_summary=_to_summary(before_summary),
        after_summary=_to_summary(after_summary),
        success=success,
        error_message=(error_message[:512] if error_message else None),
    )
    if use_own_commit:
        with auto_commit(session):
            session.add(log)
    else:
        session.add(log)


""" 列表查询 """


def list_operation_logs(
    session: Session,
    *,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
    operator_id: int | None = None,
    module: str | None = None,
    action: str | None = None,
    success: bool | None = None,
    start_time: int | None = None,  # unix 秒
    end_time: int | None = None,
) -> PageData[OperationLogListItem]:
    stmt = select(AdminOperationLog).order_by(col(AdminOperationLog.id).desc())
    if operator_id is not None:
        stmt = stmt.where(AdminOperationLog.operator_id == operator_id)
    if module:
        stmt = stmt.where(AdminOperationLog.module == module.strip())
    if action:
        stmt = stmt.where(AdminOperationLog.action == action.strip())
    if success is not None:
        stmt = stmt.where(AdminOperationLog.success == success)
    if start_time is not None:
        stmt = stmt.where(AdminOperationLog.create_time >= start_time)
    if end_time is not None:
        stmt = stmt.where(AdminOperationLog.create_time <= end_time)
    rows, total = paginate(session, stmt, page, size)
    items = []
    for r in rows:
        item = OperationLogListItem.model_validate(r)
        # item.has_detail = bool(r.before_summary or r.after_summary or r.request_summary)
        items.append(item)
    return PageData.build(items, total, page, size)


# 详情查询
def get_operation_log(session: Session, log_id: int) -> OperationLogDetail:
    row = session.get(AdminOperationLog, log_id)
    if row is None:
        raise AppError("审计日志不存在", code=404, http_status=404)
    return OperationLogDetail.model_validate(row)
