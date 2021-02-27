"""empty message

Revision ID: d0003d357b3e
Revises: 
Create Date: 2021-02-24 15:19:59.483087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0003d357b3e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('revoked_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=150), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('admin', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('public_id', sa.String(length=50), nullable=True))
    op.create_unique_constraint(None, 'user', ['public_id'])
    op.drop_column('user', 'first_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_name', sa.VARCHAR(length=150), nullable=True))
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'public_id')
    op.drop_column('user', 'admin')
    op.drop_table('revoked_token')
    # ### end Alembic commands ###