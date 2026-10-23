"""baseline schema

Revision ID: fb09e5e13678
Revises: 
Create Date: 2026-10-22 15:43:19.206226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb09e5e13678'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="user"),
    )

    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False, unique=True),
        sa.Column("ingredients", sa.String(), nullable=False),
        sa.Column("instructions", sa.String(), nullable=False, server_default=""),
        sa.Column("is_public", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_table("recipes")
    op.drop_table("users")