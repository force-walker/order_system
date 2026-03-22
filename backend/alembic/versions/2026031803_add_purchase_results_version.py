"""add version column to purchase_results

Revision ID: 2026031803
Revises: 2026031802
Create Date: 2026-03-18 00:53:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031803'
down_revision = '2026031802'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('purchase_results', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('purchase_results', 'version')
