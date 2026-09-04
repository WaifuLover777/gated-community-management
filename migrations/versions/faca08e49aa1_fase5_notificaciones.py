"""fase5 notificaciones"""
from alembic import op
import sqlalchemy as sa


revision = 'faca08e49aa1'
down_revision = 'd6141e386fce'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('notificaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('residente_id', sa.Integer(), nullable=True),
    sa.Column('titulo', sa.String(length=120), nullable=False),
    sa.Column('mensaje', sa.Text(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=True),
    sa.Column('leido', sa.Boolean(), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('notificaciones', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notificaciones_creado_en'), ['creado_en'], unique=False)
        batch_op.create_index(batch_op.f('ix_notificaciones_residente_id'), ['residente_id'], unique=False)



def downgrade():
    with op.batch_alter_table('notificaciones', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notificaciones_residente_id'))
        batch_op.drop_index(batch_op.f('ix_notificaciones_creado_en'))

    op.drop_table('notificaciones')
