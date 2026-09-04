"""fase11 rostros enrolados"""
from alembic import op
import sqlalchemy as sa


revision = '17f8d26f390c'
down_revision = '133976188fe3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('rostros',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=True),
    sa.Column('residente_id', sa.Integer(), nullable=True),
    sa.Column('embedding', sa.Text(), nullable=False),
    sa.Column('foto', sa.String(length=255), nullable=True),
    sa.Column('consentimiento', sa.Boolean(), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('rostros', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_rostros_creado_en'), ['creado_en'], unique=False)
        batch_op.create_index(batch_op.f('ix_rostros_residente_id'), ['residente_id'], unique=False)



def downgrade():
    with op.batch_alter_table('rostros', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rostros_residente_id'))
        batch_op.drop_index(batch_op.f('ix_rostros_creado_en'))

    op.drop_table('rostros')
