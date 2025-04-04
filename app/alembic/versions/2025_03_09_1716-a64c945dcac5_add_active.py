"""add active

Revision ID: a64c945dcac5
Revises: 4c3a056a45e6
Create Date: 2025-03-09 17:16:03.387845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a64c945dcac5'
down_revision: Union[str, None] = '4c3a056a45e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('referral_codes', sa.Column('active', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('referral_codes', 'active')
    # ### end Alembic commands ###
