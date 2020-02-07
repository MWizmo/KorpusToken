"""empty message

Revision ID: f8491852c9cd
Revises: 3b4fdc41286b
Create Date: 2020-02-07 17:31:13.976771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8491852c9cd'
down_revision = '3b4fdc41286b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questionnaire__table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_opened', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('questionnaire__table')
    # ### end Alembic commands ###
