"""fase4 multas"""
from alembic import op
import sqlalchemy as sa


revision = 'd6141e386fce'
down_revision = 'e50739e72598'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('multas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('motivo', sa.String(length=120), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('monto', sa.Float(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('fecha', sa.Date(), nullable=True),
    sa.Column('fecha_pago', sa.String(length=20), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('multas')
