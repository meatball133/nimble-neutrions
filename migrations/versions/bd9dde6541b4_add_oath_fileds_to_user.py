"""add oath fileds to user

Revision ID: bd9dde6541b4
Revises: a4dc71b6175a
Create Date: 2024-07-22 19:37:48.103830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd9dde6541b4'
down_revision: Union[str, None] = 'a4dc71b6175a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("access_token", sa.String(), nullable=True))
    op.add_column("user", sa.Column("refresh_token", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "refresh_token")
    op.drop_column("user", "access_token")
