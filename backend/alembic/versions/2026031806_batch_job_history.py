"""add batch job history table

Revision ID: 2026031806
Revises: 2026031805
Create Date: 2026-03-18 21:42:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '2026031806'
down_revision = '2026031805'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'batch_job_histories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('job_type', sa.String(length=64), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('requested_by', sa.String(length=64), nullable=False),
        sa.Column('requested_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('result_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.UniqueConstraint('task_id', name='uq_batch_job_histories_task_id'),
    )

    op.create_index('ix_batch_job_histories_task_id', 'batch_job_histories', ['task_id'])
    op.create_index('ix_batch_job_histories_job_type', 'batch_job_histories', ['job_type'])
    op.create_index('ix_batch_job_histories_order_id', 'batch_job_histories', ['order_id'])
    op.create_index('ix_batch_job_histories_status', 'batch_job_histories', ['status'])


def downgrade() -> None:
    op.drop_index('ix_batch_job_histories_status', table_name='batch_job_histories')
    op.drop_index('ix_batch_job_histories_order_id', table_name='batch_job_histories')
    op.drop_index('ix_batch_job_histories_job_type', table_name='batch_job_histories')
    op.drop_index('ix_batch_job_histories_task_id', table_name='batch_job_histories')
    op.drop_table('batch_job_histories')
