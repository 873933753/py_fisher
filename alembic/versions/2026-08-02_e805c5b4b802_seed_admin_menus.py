"""seed_admin_menus

Revision ID: e805c5b4b802
Revises: 78b97beda8f8
Create Date: 2026-08-02 02:10:31.518711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e805c5b4b802'
down_revision: Union[str, Sequence[str], None] = '78b97beda8f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1、先建立基础菜单
    op.execute(
        """
        INSERT INTO admin_menu (id, parent_id, title, path, component, icon, sort, menu_type, permission_code, is_deleted, create_time, update_time) VALUES
        (2, NULL, '前台用户', '/users', 'views/users/index', 'user', 10, 'menu', 'user:manage', 0, UNIX_TIMESTAMP(), NULL),
        (3, NULL, '系统管理', NULL, NULL, 'setting', 20, 'directory', NULL, 0, UNIX_TIMESTAMP(), NULL),
        (4, 3, '后台账号', '/admins', 'views/admins/index', 'team', 10, 'menu', 'admin:manage', 0, UNIX_TIMESTAMP(), NULL),
        (5, 3, '权限配置', '/rbac', 'views/rbac/index', 'safety', 20, 'menu', 'rbac:manage', 0, UNIX_TIMESTAMP(), NULL),
        (6, 3, '菜单管理', '/menu', 'views/menu/index', 'menu', 20, 'menu', 'menu:manage', 0, UNIX_TIMESTAMP(), NULL);
    """
    )
    # 2、给运营角色绑定业务目录和前台用户菜单
    op.execute(
        """
        INSERT INTO admin_role_menu (role_id, menu_id)
        SELECT r.id, m.id FROM admin_role r CROSS JOIN admin_menu m
        WHERE r.code = 'operator' AND m.id IN (2);
    """
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # 1、删除运营角色与菜单的绑定
    op.execute(
        """
        DELETE rm FROM admin_role_menu rm
        INNER JOIN admin_role r ON r.id = rm.role_id
        WHERE r.code = 'operator' AND rm.menu_id IN (2);
    """
    )
    # 2、删除基础菜单，先删除子菜单，再删除父菜单
    op.execute(
        """
        DELETE FROM admin_menu WHERE id IN (4, 5, 6);
        DELETE FROM admin_menu WHERE id IN (2, 3);
    """
    )
    pass
