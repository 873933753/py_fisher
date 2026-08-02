from typing import Literal

from pydantic import BaseModel, Field


# 菜单树节点
class MenuTreeNode(BaseModel):
    id: int
    parent_id: int | None = None
    title: str
    path: str | None = None
    component: str | None = None
    icon: str | None = None
    sort: int = 0
    menu_type: str
    permission_code: str | None = None
    children: list["MenuTreeNode"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# 角色-菜单集合，输出模型
class RoleMenuIdsOut(BaseModel):
    role_code: str
    menu_ids: list[int]


# 菜单id集合，输入模型
class RoleMenuIdsIn(BaseModel):
    menu_ids: list[int] = Field(default_factory=list)


MenuType = Literal["directory", "menu"]


# 菜单项
class MenuItem(BaseModel):
    id: int
    parent_id: int | None = None
    title: str
    path: str | None = None
    component: str | None = None
    icon: str | None = None
    sort: int = 0
    menu_type: str
    permission_code: str | None = None
    model_config = {"from_attributes": True}


# 菜单创建
class MenuCreateIn(BaseModel):
    parent_id: int | None = None
    title: str = Field(min_length=1, max_length=64)
    path: str | None = Field(default=None, max_length=128)
    component: str | None = Field(default=None, max_length=128)
    icon: str | None = Field(default=None, max_length=64)
    sort: int = 0
    menu_type: MenuType = "menu"
    permission_code: str | None = Field(default=None, max_length=64)


# 菜单修改,未传的字段不修改
class MenuUpdateIn(BaseModel):
    parent_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=64)
    path: str | None = Field(default=None, max_length=128)
    component: str | None = Field(default=None, max_length=128)
    icon: str | None = Field(default=None, max_length=64)
    sort: int | None = None
    menu_type: MenuType | None = None
    permission_code: str | None = Field(default=None, max_length=64)


""" 菜单-绑定接口关联模型 """
ALLOWED_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "*"})


# 菜单-接口项
class MenuApiItem(BaseModel):
    id: int
    menu_id: int
    method: str
    path_pattern: str
    sort: int = 0
    model_config = {"from_attributes": True}


# 菜单-接口输入
class MenuApiIn(BaseModel):
    method: str = "*"
    path_pattern: str = Field(min_length=1, max_length=255)
    sort: int = 0


# 菜单-接口批量修改输入
class MenuApisPutIn(BaseModel):
    apis: list[MenuApiIn] = Field(default_factory=list)


# 菜单-接口输出
class MenuApisOut(BaseModel):
    menu_id: int
    apis: list[MenuApiItem]
