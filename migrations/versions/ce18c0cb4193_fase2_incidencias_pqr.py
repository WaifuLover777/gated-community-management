"""fase2 incidencias pqr"""
from alembic import op
import sqlalchemy as sa


revision = 'ce18c0cb4193'
down_revision = '2bf2adb4588c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('incidencias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('residente_id', sa.Integer(), nullable=True),
    sa.Column('titulo', sa.String(length=120), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=False),
    sa.Column('categoria', sa.String(length=20), nullable=True),
    sa.Column('foto', sa.String(length=255), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('respuesta', sa.Text(), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('incidencias', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_incidencias_fecha_creacion'), ['fecha_creacion'], unique=False)



def downgrade():
    with op.batch_alter_table('incidencias', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_incidencias_fecha_creacion'))

    op.drop_table('incidencias')
