from sqlmodel import SQLModel, Field
from datetime import datetime


class SoftDeleteMixin:
    # 软删除字段 - 是否删除，0:未删除 1:已删除
    # is_deleted = Column(Integer, nullable=False, default=0, server_default="0")
    # is_deleted: int = Field(
    #     default=0,
    #     sa_column=Column(Integer, nullable=False, server_default="0"),
    # )

    is_deleted: int = Field(default=0)

    # 软删除模型方法 - 将is_deleted设置为1
    def soft_delete(self):
        self.is_deleted = 1


# 基类模型 - 所有模型都继承自这个基类
# 继承SoftDeleteMixin，实现软删除功能
class BaseModel(SQLModel, SoftDeleteMixin):
    # is_deleted: int = Field(default=0) # 0:未删除 1:已删除
    # Unix 时间戳（秒）
    # 为模型添加创建时间，默认当前时间
    create_time: int = Field(default_factory=lambda: int(datetime.now().timestamp()))

    # attrs_dict: 字典，键为属性名，值为属性值
    def set_attrs(self, attrs_dict: dict):
        for key, value in attrs_dict.items():
            # 如果属性存在且不是id，则设置属性 - 往模型中设置属性
            # 只是把属性赋到对象上，并没有写入数据库
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)
