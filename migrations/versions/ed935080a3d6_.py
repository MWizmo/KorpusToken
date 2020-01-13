"""empty message

Revision ID: ed935080a3d6
Revises: 564b0618a0a2
Create Date: 2020-01-12 20:27:56.964434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed935080a3d6'
down_revision = '564b0618a0a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('chat_id', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('state', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'state')
    op.drop_column('user', 'chat_id')
    # ### end Alembic commands ###