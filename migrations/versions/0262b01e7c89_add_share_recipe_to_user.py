"""add share_recipe to user

Revision ID: 0262b01e7c89
Revises: fb09e5e13678
Create Date: 2026-10-23 09:20:00.445929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0262b01e7c89'
down_revision = 'fb09e5e13678'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.create_foreign_key(
            "fk_recipes_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
        )

    op.add_column(
        "users",
        sa.Column("share_recipe", sa.String(), nullable=True),
    )


def downgrade():
    op.drop_column("users", "share_recipe")

    with op.batch_alter_table("recipes") as batch_op:
        batch_op.drop_constraint(
            "fk_recipes_owner_id_users",
            type_="foreignkey",
        )