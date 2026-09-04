"""fase8 visita token qr"""
from alembic import op
import sqlalchemy as sa


revision = 'b42d3fdac163'
down_revision = '27735dedcf38'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('visitas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('token', sa.String(length=32), nullable=True))
        batch_op.create_index(batch_op.f('ix_visitas_token'), ['token'], unique=True)



def downgrade():
    with op.batch_alter_table('visitas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_visitas_token'))
        batch_op.drop_column('token')

