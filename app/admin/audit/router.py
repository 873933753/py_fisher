from fastapi import APIRouter

from app.admin.audit.schemas import OperationLogDetail, OperationLogListItem
from app.admin.audit.service import get_operation_log, list_operation_logs
from app.admin.auth.schemas import ApiResponse
from app.admin.dependencies import AdminSession
from app.schemas.pagination import Page, PageData, PageSize
from app.setting import DEFAULT_PAGE_SIZE

audit_router = APIRouter(tags=["admin-audit"])


@audit_router.get(
    "/logs",
    response_model=ApiResponse[PageData[OperationLogListItem]],
    summary="操作审计日志分页列表",
)
def audit_logs_list(
    session: AdminSession,
    page: Page = 1,
    size: PageSize = DEFAULT_PAGE_SIZE,
    operator_id: int | None = None,
    module: str | None = None,
    action: str | None = None,
    success: bool | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
):
    data = list_operation_logs(
        session,
        page=page,
        size=size,
        operator_id=operator_id,
        module=module,
        action=action,
        success=success,
        start_time=start_time,
        end_time=end_time,
    )
    return ApiResponse(data=data, message="ok")


@audit_router.get(
    "/logs/{log_id}",
    response_model=ApiResponse[OperationLogDetail],
    summary="操作审计日志详情",
)
def audit_logs_detail(log_id: int, session: AdminSession):
    return ApiResponse(data=get_operation_log(session, log_id), message="ok")
