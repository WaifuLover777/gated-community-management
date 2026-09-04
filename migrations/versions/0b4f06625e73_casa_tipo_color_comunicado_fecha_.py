"""casa tipo/color, comunicado fecha_publicacion"""
from alembic import op
import sqlalchemy as sa


revision = '0b4f06625e73'
down_revision = 'ded16d47b08f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('color', sa.String(length=30), nullable=True))

    with op.batch_alter_table('comunicados', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha_publicacion', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_comunicados_fecha_publicacion'), ['fecha_publicacion'], unique=False)

    op.execute("UPDATE comunicados SET fecha_publicacion = publicado_en "
               "WHERE fecha_publicacion IS NULL")



def downgrade():
    with op.batch_alter_table('comunicados', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comunicados_fecha_publicacion'))
        batch_op.drop_column('fecha_publicacion')

    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.drop_column('color')
        batch_op.drop_column('tipo')

