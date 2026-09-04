"""casa pin_registro"""
from alembic import op
import sqlalchemy as sa


revision = 'a1c2e3f4b5d6'
down_revision = '0b4f06625e73'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pin_registro', sa.String(length=6), nullable=True))
        batch_op.create_index(batch_op.f('ix_casas_pin_registro'), ['pin_registro'], unique=False)


def downgrade():
    with op.batch_alter_table('casas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_casas_pin_registro'))
        batch_op.drop_column('pin_registro')
