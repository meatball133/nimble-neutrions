"""rename content table to attachment

Revision ID: 3667668fc3a2
Revises: 323b5df7278e
Create Date: 2024-07-22 11:52:16.599202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3667668fc3a2'
down_revision: Union[str, None] = '323b5df7278e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass