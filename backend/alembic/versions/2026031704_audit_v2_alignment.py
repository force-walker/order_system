"""align audit indexes to MVP v2

Revision ID: 2026031704
Revises: 2026031703
Create Date: 2026-03-17 23:08:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031704'
down_revision = '2026031703'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # keep existing structure but add v2-focused composite indexes
    op.create_index('ix_audit_entity_changed_at', 'audit_logs', ['entity_type', 'entity_id', 'changed_at'])
    op.create_index('ix_audit_changed_by_changed_at', 'audit_logs', ['changed_by', 'changed_at'])


def downgrade() -> None:
    op.drop_index('ix_audit_changed_by_changed_at', table_name='audit_logs')
    op.drop_index('ix_audit_entity_changed_at', table_name='audit_logs')
