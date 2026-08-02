"""seed_rbac_manage_permission

Revision ID: d8d3812a4a27
Revises: 6e96224ea173
Create Date: 2026-08-01 00:57:36.051763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8d3812a4a27'
down_revision: Union[str, Sequence[str], None] = '6e96224ea173'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO admin_permission (id, code, name, group_name, is_deleted, create_time, update_time)
        VALUES (10, 'rbac:manage', '权限配置', 'rbac', 0, UNIX_TIMESTAMP(), NULL)
        """
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
