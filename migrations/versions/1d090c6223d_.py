"""empty message

Revision ID: 1d090c6223d
Revises: 4d92a799d28
Create Date: 2016-11-29 18:14:46.428805

"""

# revision identifiers, used by Alembic.
revision = '1d090c6223d'
down_revision = '4d92a799d28'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('financial_accounts',
    sa.Column('pk_n', sa.Integer(), nullable=False),
    sa.Column('user_pk', sa.Integer(), nullable=True),
    sa.Column('club_pk', sa.Integer(), nullable=True),
    sa.Column('money_nn', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['club_pk'], ['clubs.club_id_n'], ),
    sa.ForeignKeyConstraint(['user_pk'], ['users.pk'], ),
    sa.PrimaryKeyConstraint('pk_n')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('financial_accounts')
    ### end Alembic commands ###