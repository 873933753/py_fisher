from pydantic import BaseModel, Field


class RoleItem(BaseModel):
    id: int
    code: str
    name: str
    model_config = {"from_attributes": True}


class PermissionItem(BaseModel):
    id: int
    code: str
    name: str
    group_name: str
    model_config = {"from_attributes": True}


class RolePermissionCodesOut(BaseModel):
    role_code: str
    codes: list[str]


class RolePermissionCodesIn(BaseModel):
    codes: list[str] = Field(default_factory=list)
