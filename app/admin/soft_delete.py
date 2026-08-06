from sqlmodel import Field


# 不要继承 SQLModel，只做 mixin
class SoftDeleteMixin:
    is_deleted: int = Field(default=0)

    def soft_delete(self) -> None:
        self.is_deleted = 1
