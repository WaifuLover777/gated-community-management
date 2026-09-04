"""fase10 placas anti-passback lista negra"""
from alembic import op
import sqlalchemy as sa


revision = '133976188fe3'
down_revision = '92f879fcd2cf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('lista_negra',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('placa', sa.String(length=15), nullable=False),
    sa.Column('motivo', sa.String(length=200), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('lista_negra', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_lista_negra_placa'), ['placa'], unique=True)

    with op.batch_alter_table('accesos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('placa_frontal', sa.String(length=15), nullable=True))
        batch_op.add_column(sa.Column('placa_trasera', sa.String(length=15), nullable=True))
        batch_op.add_column(sa.Column('metodo', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('confianza', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('foto_evidencia', sa.String(length=255), nullable=True))



def downgrade():
    with op.batch_alter_table('accesos', schema=None) as batch_op:
        batch_op.drop_column('foto_evidencia')
        batch_op.drop_column('confianza')
        batch_op.drop_column('metodo')
        batch_op.drop_column('placa_trasera')
        batch_op.drop_column('placa_frontal')

    with op.batch_alter_table('lista_negra', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_lista_negra_placa'))

    op.drop_table('lista_negra')
