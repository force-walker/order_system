"""add invoice lock fields for unlock/reset policy

Revision ID: 2026031801
Revises: 2026031704
Create Date: 2026-03-18 00:23:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031801'
down_revision = '2026031704'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('invoices', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('invoices', sa.Column('locked_at', sa.DateTime(), nullable=True))
    op.create_index('ix_invoices_is_locked', 'invoices', ['is_locked'])


def downgrade() -> None:
    op.drop_index('ix_invoices_is_locked', table_name='invoices')
    op.drop_column('invoices', 'locked_at')
    op.drop_column('invoices', 'is_locked')
