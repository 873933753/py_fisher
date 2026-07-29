from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria
from sqlmodel import Session

from app.admin.base import AdminBaseModel


# 监听SQL执行，过滤软删除数据 - 后台管理
@event.listens_for(Session, "do_orm_execute")
def _filter_admin_soft_deleted(execute_state):
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                AdminBaseModel,
                lambda cls: cls.is_deleted == 0,
                include_aliases=True,
            )
        )
