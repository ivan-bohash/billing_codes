"""delete details

Revision ID: 84968c2f56ce
Revises: 9d079c7455db
Create Date: 2025-05-05 16:08:05.025566

"""
from typing import Sequence, Union

import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84968c2f56ce'
down_revision: Union[str, None] = '9d079c7455db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema"""
    op.drop_index('ix_details_billable_icd_code', table_name='details_billable')
    op.drop_table('details_billable')

    op.drop_index('ix_details_non_billable_icd_code', table_name='details_non_billable')
    op.drop_table('details_non_billable')


def downgrade() -> None:
    """Downgrade schema"""

    op.create_table(
        'details_billable',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=False),
        sa.Column('updated_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=False),
        sa.Column('icd_codes', sa.String(), nullable=False),
        sa.Column('detail', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_details_billable_icd_code', 'details_billable', ['icd_codes'], unique=False)

    op.create_table(
        'details_non_billable',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=False),
        sa.Column('updated_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=False),
        sa.Column('icd_codes', sa.String(), nullable=False),
        sa.Column('detail', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_details_non_billable_icd_code', 'details_non_billable', ['icd_codes'], unique=False)
