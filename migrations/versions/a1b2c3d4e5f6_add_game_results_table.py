"""add game_results table

Revision ID: a1b2c3d4e5f6
Revises: c151da14ba0c
Create Date: 2026-04-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'c151da14ba0c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'game_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game', sa.String(length=50), nullable=False),
        sa.Column('winner', sa.String(length=50), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('played_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                name=op.f('fk_game_results_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_game_results'))
    )


def downgrade():
    op.drop_table('game_results')
