"""seed_admin_rbac

Revision ID: 6e96224ea173
Revises: 9b0042cc36c2
Create Date: 2026-08-01 00:33:57.275265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e96224ea173'
down_revision: Union[str, Sequence[str], None] = '9b0042cc36c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 角色
    op.execute(
        """
        INSERT INTO admin_role (id, code, name, is_deleted, create_time, update_time) VALUES
        (1, 'super_admin', '超级管理员', 0, UNIX_TIMESTAMP(), NULL),
        (2, 'operator', '运营', 0, UNIX_TIMESTAMP(), NULL)
        """
    )
    # 权限
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
    # 运营绑定
    op.execute(
        """
        INSERT INTO admin_role_permission (role_id, permission_id) VALUES
        (2, 1), (2, 2), (2, 9)
        """
    )
def downgrade() -> None:
    op.execute("DELETE FROM admin_role_permission")
    op.execute("DELETE FROM admin_permission")
    op.execute("DELETE FROM admin_role")
