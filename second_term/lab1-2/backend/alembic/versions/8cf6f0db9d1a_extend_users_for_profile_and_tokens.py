"""extend users for profile and tokens

Revision ID: 8cf6f0db9d1a
Revises: a613d8962236
Create Date: 2026-03-13 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8cf6f0db9d1a"
down_revision: Union[str, Sequence[str], None] = "a613d8962236"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=255), server_default="admin@example.com", nullable=False))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), server_default="Admin", nullable=False))
    op.add_column("users", sa.Column("first_name", sa.String(length=100), server_default="User", nullable=False))
    op.add_column("users", sa.Column("middle_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("default_page_size", sa.Integer(), server_default="20", nullable=False))
    op.add_column("users", sa.Column("auto_refresh_seconds", sa.Integer(), server_default="0", nullable=False))
    op.add_column("users", sa.Column("default_language", sa.String(length=2), server_default="ru", nullable=False))
    op.add_column("users", sa.Column("token_version", sa.Integer(), server_default="0", nullable=False))
    op.create_unique_constraint("uq_users_email", "users", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_column("users", "token_version")
    op.drop_column("users", "default_language")
    op.drop_column("users", "auto_refresh_seconds")
    op.drop_column("users", "default_page_size")
    op.drop_column("users", "middle_name")
    op.drop_column("users", "first_name")
    op.drop_column("users", "last_name")
    op.drop_column("users", "email")
