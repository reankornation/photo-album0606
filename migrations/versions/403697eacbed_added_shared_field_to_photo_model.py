"""Added shared field to Photo model

Revision ID: 403697eacbed
Revises: a3891430b128
Create Date: 2025-03-10 19:29:03.423995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '403697eacbed'
down_revision = 'a3891430b128'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('photo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shared', sa.Boolean(), nullable=True))
        batch_op.alter_column('album_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('photo', schema=None) as batch_op:
        batch_op.alter_column('album_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('shared')

    # ### end Alembic commands ###
