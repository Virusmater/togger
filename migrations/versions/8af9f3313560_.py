"""empty message

Revision ID: 8af9f3313560
Revises: 8d0d09f3990a
Create Date: 2020-07-02 20:53:13.932702

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '8af9f3313560'
down_revision = '8d0d09f3990a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('hide', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event', 'hide')
    # ### end Alembic commands ###