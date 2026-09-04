"""fase1 bitacora novedades guardia"""
from alembic import op
import sqlalchemy as sa


revision = '2bf2adb4588c'
down_revision = 'eef3c7084f20'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('novedades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha_hora', sa.DateTime(), nullable=True),
    sa.Column('categoria', sa.String(length=20), nullable=True),
    sa.Column('texto', sa.Text(), nullable=False),
    sa.Column('foto', sa.String(length=255), nullable=True),
    sa.Column('tipo', sa.String(length=20), nullable=True),
    sa.Column('guardia_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guardia_id'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('novedades', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_novedades_fecha_hora'), ['fecha_hora'], unique=False)



def downgrade():
    with op.batch_alter_table('novedades', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_novedades_fecha_hora'))

    op.drop_table('novedades')
