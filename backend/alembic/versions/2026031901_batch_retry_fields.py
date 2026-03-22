"""add retry tracking fields to batch_job_histories

Revision ID: 2026031901
Revises: 2026031806
Create Date: 2026-03-19 09:58:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031901'
down_revision = '2026031806'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('batch_job_histories', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('batch_job_histories', sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'))
    op.add_column('batch_job_histories', sa.Column('parent_task_id', sa.String(length=64), nullable=True))
    op.create_index('ix_batch_job_histories_parent_task_id', 'batch_job_histories', ['parent_task_id'])


def downgrade() -> None:
    op.drop_index('ix_batch_job_histories_parent_task_id', table_name='batch_job_histories')
    op.drop_column('batch_job_histories', 'parent_task_id')
    op.drop_column('batch_job_histories', 'max_retries')
    op.drop_column('batch_job_histories', 'retry_count')
