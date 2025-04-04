"""Cambio de Imagenes a varias imagenes

Revision ID: cc6cf780deaf
Revises: 9fd4b11af869
Create Date: 2025-03-28 01:15:32.367957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc6cf780deaf'
down_revision = '9fd4b11af869'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('imagen',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('noticia_id', sa.Integer(), nullable=False),
    sa.Column('archivo', sa.String(length=300), nullable=False),
    sa.ForeignKeyConstraint(['noticia_id'], ['noticia.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('noticia', schema=None) as batch_op:
        batch_op.drop_column('imagen')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('noticia', schema=None) as batch_op:
        batch_op.add_column(sa.Column('imagen', sa.VARCHAR(length=300), autoincrement=False, nullable=True))

    op.drop_table('imagen')
    # ### end Alembic commands ###
