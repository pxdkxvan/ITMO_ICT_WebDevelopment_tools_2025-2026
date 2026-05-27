"""initial finance schema

Revision ID: 0001_init_finance_schema
Revises:
Create Date: 2026-04-15 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op


revision = "0001_init_finance_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=False)

    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", "kind", name="uq_user_category"),
    )
    op.create_index(op.f("ix_category_user_id"), "category", ["user_id"], unique=False)

    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_user_tag"),
    )
    op.create_index(op.f("ix_tag_user_id"), "tag", ["user_id"], unique=False)

    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transaction_user_id"), "transaction", ["user_id"], unique=False)
    op.create_index(op.f("ix_transaction_category_id"), "transaction", ["category_id"], unique=False)

    op.create_table(
        "budget",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("month", sa.String(), nullable=False),
        sa.Column("limit_amount", sa.Float(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category_id", "month", name="uq_budget_month"),
    )
    op.create_index(op.f("ix_budget_user_id"), "budget", ["user_id"], unique=False)
    op.create_index(op.f("ix_budget_category_id"), "budget", ["category_id"], unique=False)

    op.create_table(
        "goal",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("target_amount", sa.Float(), nullable=False),
        sa.Column("current_amount", sa.Float(), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_goal_user_id"), "goal", ["user_id"], unique=False)

    op.create_table(
        "transactiontaglink",
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transaction.id"]),
        sa.PrimaryKeyConstraint("transaction_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("transactiontaglink")

    op.drop_index(op.f("ix_goal_user_id"), table_name="goal")
    op.drop_table("goal")

    op.drop_index(op.f("ix_budget_category_id"), table_name="budget")
    op.drop_index(op.f("ix_budget_user_id"), table_name="budget")
    op.drop_table("budget")

    op.drop_index(op.f("ix_transaction_category_id"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_user_id"), table_name="transaction")
    op.drop_table("transaction")

    op.drop_index(op.f("ix_tag_user_id"), table_name="tag")
    op.drop_table("tag")

    op.drop_index(op.f("ix_category_user_id"), table_name="category")
    op.drop_table("category")

    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
