"""add opponent_id to game_results

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-04-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a1'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('game_results',
        sa.Column('opponent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_game_results_opponent_id_users',
        'game_results', 'users',
        ['opponent_id'], ['id']
    )


def downgrade():
    op.drop_constraint('fk_game_results_opponent_id_users', 'game_results', type_='foreignkey')
    op.drop_column('game_results', 'opponent_id')
