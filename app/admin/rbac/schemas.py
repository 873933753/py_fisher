from pydantic import BaseModel, Field


class RoleItem(BaseModel):
    id: int
    code: str
    name: str
    model_config = {"from_attributes": True}


class RoleCreateIn(BaseModel):
    code: str = Field(min_length=1, max_length=32)  # 建议只允许 [a-z0-9_]
    name: str = Field(min_length=1, max_length=64)


class RoleUpdateIn(BaseModel):
    # code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=64)
