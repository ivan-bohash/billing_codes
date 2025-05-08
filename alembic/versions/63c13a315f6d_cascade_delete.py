"""cascade delete

Revision ID: 63c13a315f6d
Revises: 3e961ec66213
Create Date: 2025-05-08 16:39:03.659960

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '63c13a315f6d'
down_revision: Union[str, None] = '3e961ec66213'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('history_billable', schema=None) as batch_op:
        batch_op.drop_constraint('fk_history_billable_url_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_history_billable_url_id',
            'urls_billable',
            ['url_id'],
            ['id'],
            ondelete='CASCADE'
        )

    with op.batch_alter_table('history_non_billable', schema=None) as batch_op:
        batch_op.drop_constraint('fk_history_non_billable_url_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_history_non_billable_url_id',
            'urls_non_billable',
            ['url_id'],
            ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('history_billable', schema=None) as batch_op:
        batch_op.drop_constraint('fk_history_billable_url_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_history_billable_url_id',
            'urls_billable',
            ['url_id'],
            ['id']
        )

    with op.batch_alter_table('history_non_billable', schema=None) as batch_op:
        batch_op.drop_constraint('fk_history_non_billable_url_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_history_non_billable_url_id',
            'urls_non_billable',
            ['url_id'],
            ['id']
        )
