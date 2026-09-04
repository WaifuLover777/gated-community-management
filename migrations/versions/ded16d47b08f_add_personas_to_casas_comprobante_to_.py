"""add_personas_to_casas_comprobante_to_cuotas"""
from alembic import op
import sqlalchemy as sa


revision = 'ded16d47b08f'
down_revision = '086fda99f3d8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('personas', sa.Integer(), nullable=True))

    with op.batch_alter_table('cuotas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comprobante', sa.String(length=200), nullable=True))



def downgrade():
    with op.batch_alter_table('cuotas', schema=None) as batch_op:
        batch_op.drop_column('comprobante')

    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.drop_column('personas')

