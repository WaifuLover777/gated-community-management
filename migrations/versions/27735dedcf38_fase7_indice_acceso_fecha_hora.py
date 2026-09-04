"""fase7 indice acceso fecha_hora"""
from alembic import op
import sqlalchemy as sa


revision = '27735dedcf38'
down_revision = 'c83d40125936'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('accesos', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_accesos_fecha_hora'), ['fecha_hora'], unique=False)



def downgrade():
    with op.batch_alter_table('accesos', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_accesos_fecha_hora'))

