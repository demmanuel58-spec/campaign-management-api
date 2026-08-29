"""Initial schema revision with RBAC, Clients, Campaigns, Tasks, Activity Logs, and Indexes

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-29

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'MANAGER', 'VIEWER', name='userrole', native_enum=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)

    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'PLANNING', 'ACTIVE', 'COMPLETED', 'CANCELLED', name='campaignstatus', native_enum=False), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index('idx_campaign_status_deleted', 'campaigns', ['status', 'is_deleted'], unique=False)
    op.create_index('idx_campaign_creator', 'campaigns', ['created_by'], unique=False)
    op.create_index('idx_campaign_client', 'campaigns', ['client_id'], unique=False)

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('TODO', 'IN_PROGRESS', 'REVIEW', 'DONE', name='taskstatus', native_enum=False), nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('assigned_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index('idx_task_campaign', 'tasks', ['campaign_id'], unique=False)
    op.create_index('idx_task_assigned_user', 'tasks', ['assigned_user_id'], unique=False)

    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)
    op.create_index('idx_log_user', 'activity_logs', ['user_id'], unique=False)
    op.create_index('idx_log_campaign', 'activity_logs', ['campaign_id'], unique=False)

def downgrade() -> None:
    op.drop_index('idx_log_campaign', table_name='activity_logs')
    op.drop_index('idx_log_user', table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_table('activity_logs')

    op.drop_index('idx_task_assigned_user', table_name='tasks')
    op.drop_index('idx_task_campaign', table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')

    op.drop_index('idx_campaign_client', table_name='campaigns')
    op.drop_index('idx_campaign_creator', table_name='campaigns')
    op.drop_index('idx_campaign_status_deleted', table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_table('campaigns')

    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_table('clients')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
