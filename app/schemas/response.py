from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


# 通用响应模型
# code: 响应码，0表示成功，其他表示错误
# message: 响应消息，默认为'ok'
# data: 响应数据，泛型T，默认为None
# 不能放普通的模型，因为普通模型不能被序列化
# 只能放Pydantic模型，因为Pydantic模型可以被序列化
class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: Optional[T] = None
