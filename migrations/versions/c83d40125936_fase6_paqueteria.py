"""fase6 paqueteria"""
from alembic import op
import sqlalchemy as sa


revision = 'c83d40125936'
down_revision = 'faca08e49aa1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('paquetes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('descripcion', sa.String(length=200), nullable=False),
    sa.Column('remitente', sa.String(length=120), nullable=True),
    sa.Column('foto', sa.String(length=255), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('recibido_por', sa.String(length=120), nullable=True),
    sa.Column('retirado_por', sa.String(length=120), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=True),
    sa.Column('fecha_entrega', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('paquetes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_paquetes_creado_en'), ['creado_en'], unique=False)



def downgrade():
    with op.batch_alter_table('paquetes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_paquetes_creado_en'))

    op.drop_table('paquetes')
