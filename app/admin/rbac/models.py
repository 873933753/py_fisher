from typing import Optional

from sqlmodel import Field, SQLModel

from app.admin.base import AdminBaseModel


# 角色模型
class AdminRole(AdminBaseModel, table=True):
    __tablename__ = "admin_role"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=32, unique=True, index=True)  # super_admin / operator
    name: str = Field(max_length=64)


# 菜单模型
class AdminMenu(AdminBaseModel, table=True):
    __tablename__ = "admin_menu"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(
        default=None, foreign_key="admin_menu.id", index=True
    )
    title: str = Field(max_length=64)
    path: Optional[str] = Field(default=None, max_length=128)  # 前端路由
    component: Optional[str] = Field(default=None, max_length=128)  # 前端组件
    icon: Optional[str] = Field(default=None, max_length=64)
    sort: int = Field(default=0)
    menu_type: str = Field(default="menu", max_length=16)  # directory | menu


# 角色-菜单关联模型
class AdminRoleMenu(SQLModel, table=True):
    __tablename__ = "admin_role_menu"

    role_id: int = Field(foreign_key="admin_role.id", primary_key=True)
    menu_id: int = Field(foreign_key="admin_menu.id", primary_key=True)


# 菜单-接口关联模型
class AdminMenuApi(AdminBaseModel, table=True):
    """菜单绑定的接口"""

    __tablename__ = "admin_menu_api"

    id: Optional[int] = Field(default=None, primary_key=True)
    menu_id: int = Field(foreign_key="admin_menu.id", index=True)
    method: str = Field(max_length=16, default="*")  # GET/POST/PUT/PATCH/DELETE/*
    path_pattern: str = Field(max_length=255)  # /admin/users 或 /admin/users/**
    sort: int = Field(default=0)
    remark: Optional[str] = Field(default=None, max_length=255)


# 角色-菜单接口关联模型
class AdminRoleMenuApi(SQLModel, table=True):
    """角色拥有的菜单接口（角色勾选 API）。"""

    __tablename__ = "admin_role_menu_api"

    role_id: int = Field(foreign_key="admin_role.id", primary_key=True)
    menu_api_id: int = Field(foreign_key="admin_menu_api.id", primary_key=True)
