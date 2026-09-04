"""fase3 reservas areas comunes"""
from alembic import op
import sqlalchemy as sa


revision = 'e50739e72598'
down_revision = 'ce18c0cb4193'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('areas_comunes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=80), nullable=False),
    sa.Column('descripcion', sa.String(length=255), nullable=True),
    sa.Column('hora_apertura', sa.String(length=5), nullable=True),
    sa.Column('hora_cierre', sa.String(length=5), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reservas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('area_id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('residente_id', sa.Integer(), nullable=True),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('hora_inicio', sa.String(length=5), nullable=False),
    sa.Column('hora_fin', sa.String(length=5), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['area_id'], ['areas_comunes.id'], ),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('reservas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reservas_fecha'), ['fecha'], unique=False)



def downgrade():
    with op.batch_alter_table('reservas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reservas_fecha'))

    op.drop_table('reservas')
    op.drop_table('areas_comunes')
