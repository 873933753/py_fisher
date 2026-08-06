from pydantic import BaseModel


class OperationLogListItem(BaseModel):
    """列表：不带大摘要，减轻载荷"""

    id: int
    operator_id: int | None = None
    operator_name: str | None = None
    operator_role: str | None = None
    module: str
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    method: str | None = None
    path: str | None = None
    ip: str | None = None
    success: bool
    error_message: str | None = None
    create_time: int
    model_config = {"from_attributes": True}


class OperationLogDetail(OperationLogListItem):
    """详情：含全文摘要"""

    request_summary: str | None = None
    before_summary: str | None = None
    after_summary: str | None = None
    user_agent: str | None = None
    model_config = {"from_attributes": True}
