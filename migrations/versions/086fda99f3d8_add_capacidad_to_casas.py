"""add capacidad to casas"""
from alembic import op
import sqlalchemy as sa


revision = '086fda99f3d8'
down_revision = 'de1b8a7b4ed9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('capacidad', sa.Integer(), nullable=True))



def downgrade():
    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.drop_column('capacidad')

