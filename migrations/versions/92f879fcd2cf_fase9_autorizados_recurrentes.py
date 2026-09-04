"""fase9 autorizados recurrentes"""
from alembic import op
import sqlalchemy as sa


revision = '92f879fcd2cf'
down_revision = 'b42d3fdac163'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('autorizados',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('residente_id', sa.Integer(), nullable=True),
    sa.Column('nombre', sa.String(length=120), nullable=False),
    sa.Column('cedula', sa.String(length=20), nullable=True),
    sa.Column('relacion', sa.String(length=40), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=False),
    sa.Column('vigencia_desde', sa.Date(), nullable=True),
    sa.Column('vigencia_hasta', sa.Date(), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('autorizados', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_autorizados_token'), ['token'], unique=True)



def downgrade():
    with op.batch_alter_table('autorizados', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_autorizados_token'))

    op.drop_table('autorizados')
