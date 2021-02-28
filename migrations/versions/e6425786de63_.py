"""empty message

Revision ID: e6425786de63
Revises: 0859053b587a
Create Date: 2021-02-28 01:52:10.298125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6425786de63'
down_revision = '0859053b587a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'admin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('admin', sa.BOOLEAN(), nullable=True))
    # ### end Alembic commands ###