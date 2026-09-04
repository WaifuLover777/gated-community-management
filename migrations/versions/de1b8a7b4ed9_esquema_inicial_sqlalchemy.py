"""esquema inicial SQLAlchemy"""
from alembic import op
import sqlalchemy as sa


revision = 'de1b8a7b4ed9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('casas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('numero', sa.String(length=20), nullable=False),
    sa.Column('manzana', sa.String(length=20), nullable=True),
    sa.Column('villa', sa.String(length=20), nullable=True),
    sa.Column('area_m2', sa.Float(), nullable=True),
    sa.Column('alicuota', sa.Float(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero')
    )
    op.create_table('comunicados',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('titulo', sa.String(length=150), nullable=False),
    sa.Column('contenido', sa.Text(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=True),
    sa.Column('publicado_en', sa.DateTime(), nullable=True),
    sa.Column('publicado_por', sa.String(length=120), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cuotas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('mes', sa.Integer(), nullable=False),
    sa.Column('anio', sa.Integer(), nullable=False),
    sa.Column('monto', sa.Float(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('fecha_pago', sa.String(length=20), nullable=True),
    sa.Column('metodo_pago', sa.String(length=30), nullable=True),
    sa.Column('observacion', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('casa_id', 'mes', 'anio')
    )
    op.create_table('residentes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=120), nullable=False),
    sa.Column('cedula', sa.String(length=20), nullable=False),
    sa.Column('telefono', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('fecha_ingreso', sa.Date(), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.Column('foto', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cedula')
    )
    op.create_table('visitas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('nombre_visitante', sa.String(length=120), nullable=False),
    sa.Column('cedula_visitante', sa.String(length=20), nullable=True),
    sa.Column('motivo', sa.String(length=200), nullable=True),
    sa.Column('placa_vehiculo', sa.String(length=15), nullable=True),
    sa.Column('pin', sa.String(length=6), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('autorizado_por', sa.String(length=120), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.Column('fecha_entrada', sa.DateTime(), nullable=True),
    sa.Column('fecha_salida', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('visitas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_visitas_pin'), ['pin'], unique=False)

    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('rol', sa.String(length=20), nullable=True),
    sa.Column('residente_id', sa.Integer(), nullable=True),
    sa.Column('foto', sa.String(length=255), nullable=True),
    sa.Column('creado_en', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('vehiculos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('residente_id', sa.Integer(), nullable=False),
    sa.Column('placa', sa.String(length=15), nullable=False),
    sa.Column('marca', sa.String(length=50), nullable=True),
    sa.Column('modelo', sa.String(length=50), nullable=True),
    sa.Column('color', sa.String(length=30), nullable=True),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('placa')
    )
    op.create_table('accesos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=True),
    sa.Column('fecha_hora', sa.DateTime(), nullable=True),
    sa.Column('resultado', sa.String(length=20), nullable=True),
    sa.Column('observacion', sa.Text(), nullable=True),
    sa.Column('placa', sa.String(length=15), nullable=True),
    sa.Column('guardia_id', sa.Integer(), nullable=True),
    sa.Column('residente_id', sa.Integer(), nullable=True),
    sa.Column('visita_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guardia_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['residente_id'], ['residentes.id'], ),
    sa.ForeignKeyConstraint(['visita_id'], ['visitas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('accesos')
    op.drop_table('vehiculos')
    op.drop_table('usuarios')
    with op.batch_alter_table('visitas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_visitas_pin'))

    op.drop_table('visitas')
    op.drop_table('residentes')
    op.drop_table('cuotas')
    op.drop_table('comunicados')
    op.drop_table('casas')
