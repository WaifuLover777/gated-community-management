"""mora y cuotas extraordinarias"""
from alembic import op
import sqlalchemy as sa


revision = 'eef3c7084f20'
down_revision = 'a1c2e3f4b5d6'
branch_labels = None
depends_on = None

naming_convention = {"uq": "uq_%(table_name)s_%(column_0_name)s"}


def upgrade():
    with op.batch_alter_table('cuotas', schema=None,
                              naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column('tipo', sa.String(length=20),
                                      nullable=False, server_default='ordinaria'))
        batch_op.add_column(sa.Column('concepto', sa.String(length=80),
                                      nullable=False, server_default=''))
        batch_op.add_column(sa.Column('recargo', sa.Float(),
                                      nullable=True, server_default='0'))
        batch_op.drop_constraint('uq_cuotas_casa_id', type_='unique')
        batch_op.create_unique_constraint(
            'uq_cuotas_casa_id_mes_anio_concepto',
            ['casa_id', 'mes', 'anio', 'concepto'])


def downgrade():
    with op.batch_alter_table('cuotas', schema=None,
                              naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint('uq_cuotas_casa_id_mes_anio_concepto', type_='unique')
        batch_op.create_unique_constraint('uq_cuotas_casa_id', ['casa_id', 'mes', 'anio'])
        batch_op.drop_column('recargo')
        batch_op.drop_column('concepto')
        batch_op.drop_column('tipo')
