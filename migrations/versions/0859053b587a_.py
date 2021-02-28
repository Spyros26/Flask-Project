"""empty message

Revision ID: 0859053b587a
Revises: d68697918df8
Create Date: 2021-02-27 19:54:24.145233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0859053b587a'
down_revision = 'd68697918df8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dummy_table')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dummy_table',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###