"""Initial migration

Revision ID: 4cb7ac4ecf0c
Revises: 80a5ef3e3701
Create Date: 2025-02-21 15:45:27.458337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cb7ac4ecf0c'
down_revision: Union[str, None] = '80a5ef3e3701'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
