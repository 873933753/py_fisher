"""migrate_module_permissions

Revision ID: 1a7ed6cbedf6
Revises: d8d3812a4a27
Create Date: 2026-08-02 01:00:10.213681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a7ed6cbedf6'
down_revision: Union[str, Sequence[str], None] = 'd8d3812a4a27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. 清除运营角色的所有权限绑定
    op.execute(
        """
        DELETE arp FROM admin_role_permission arp
        INNER JOIN admin_role ar ON ar.id = arp.role_id
        WHERE ar.code = 'operator'
        """
    )
    # 2. 插入新的 manage 权限（id 接在 rbac:manage 的 10 后面）
    op.execute(
        """
        INSERT INTO admin_permission (id, code, name, group_name, is_deleted, create_time, update_time) VALUES
        (11, 'user:manage', '前台用户管理', 'user', 0, UNIX_TIMESTAMP(), NULL),
        (12, 'admin:manage', '后台账号管理', 'admin', 0, UNIX_TIMESTAMP(), NULL),
        (13, 'upload:manage', '上传管理', 'upload', 0, UNIX_TIMESTAMP(), NULL)
        """
    )
    # 3. 给运营角色绑定新权限
    op.execute(
        """
        INSERT INTO admin_role_permission (role_id, permission_id)
        SELECT r.id, p.id
        FROM admin_role r
        CROSS JOIN admin_permission p
        WHERE r.code = 'operator'
          AND p.code IN ('user:manage', 'admin:manage', 'upload:manage')
        """
    )
    # 4. （推荐）删除已不再使用的旧细粒度权限
    op.execute(
        """
        DELETE FROM admin_permission
        WHERE code IN (
            'user:list', 'user:detail', 'user:update', 'user:delete',
            'admin:list', 'admin:create', 'admin:update', 'admin:delete',
            'upload:image'
        )
        """
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # 1. 解除运营与新权限的绑定
    op.execute(
        """
        DELETE arp FROM admin_role_permission arp
        INNER JOIN admin_role ar ON ar.id = arp.role_id
        INNER JOIN admin_permission ap ON ap.id = arp.permission_id
        WHERE ar.code = 'operator'
          AND ap.code IN ('user:manage', 'admin:manage', 'upload:manage')
        """
    )
    # 2. 删除新权限
    op.execute(
        """
        DELETE FROM admin_permission
        WHERE code IN ('user:manage', 'admin:manage', 'upload:manage')
        """
    )
    # 3. 恢复旧权限定义（与 6e96224ea173 一致）
    op.execute(
        """
        INSERT INTO admin_permission (id, code, name, group_name, is_deleted, create_time, update_time) VALUES
        (1, 'user:list', '前台用户列表', 'user', 0, UNIX_TIMESTAMP(), NULL),
        (2, 'user:detail', '前台用户详情', 'user', 0, UNIX_TIMESTAMP(), NULL),
        (3, 'user:update', '前台用户更新', 'user', 0, UNIX_TIMESTAMP(), NULL),
        (4, 'user:delete', '前台用户删除', 'user', 0, UNIX_TIMESTAMP(), NULL),
        (5, 'admin:list', '后台账号列表', 'admin', 0, UNIX_TIMESTAMP(), NULL),
        (6, 'admin:create', '后台账号创建', 'admin', 0, UNIX_TIMESTAMP(), NULL),
        (7, 'admin:update', '后台账号更新', 'admin', 0, UNIX_TIMESTAMP(), NULL),
        (8, 'admin:delete', '后台账号删除', 'admin', 0, UNIX_TIMESTAMP(), NULL),
        (9, 'upload:image', '上传图片', 'upload', 0, UNIX_TIMESTAMP(), NULL)
        """
    )
    # 4. 恢复运营原来的权限绑定
    op.execute(
        """
        INSERT INTO admin_role_permission (role_id, permission_id) VALUES
        (2, 1), (2, 2), (2, 9)
        """
    )
    pass
