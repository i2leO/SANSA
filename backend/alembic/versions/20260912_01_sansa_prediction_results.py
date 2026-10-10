"""Add prediction results to an existing SANSA database.

Revision ID: 20260912_01
Revises: None (repository has no previous revisions)
Requires the pre-existing visits table. This is not a full schema bootstrap.
"""
from alembic import op
import sqlalchemy as sa

revision = "20260912_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sansa_prediction_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visit_id", sa.Integer(), sa.ForeignKey("visits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("age_group01", sa.Integer(), nullable=False),
        sa.Column("d2_total", sa.DECIMAL(12, 4), nullable=False),
        sa.Column("d3_total", sa.DECIMAL(12, 4), nullable=False),
        sa.Column("waist_cm", sa.DECIMAL(12, 4), nullable=False),
        sa.Column("l_over", sa.DECIMAL(24, 12), nullable=False),
        sa.Column("l_normal", sa.DECIMAL(24, 12), nullable=False),
        sa.Column("p_under", sa.DECIMAL(18, 16), nullable=False),
        sa.Column("p_normal", sa.DECIMAL(18, 16), nullable=False),
        sa.Column("p_over", sa.DECIMAL(18, 16), nullable=False),
        sa.Column("predicted_group", sa.Enum(
            "UNDER", "NORMAL", "OVER", name="sansa_prediction_group",
            create_constraint=True, validate_strings=True,
        ), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("visit_id", "model_version", name="uq_sansa_prediction_visit_version"),
        sa.CheckConstraint("age_group01 IN (0, 1)", name="ck_sansa_prediction_age_group"),
        sa.CheckConstraint(
            "p_under BETWEEN 0 AND 1 AND p_normal BETWEEN 0 AND 1 AND p_over BETWEEN 0 AND 1",
            name="ck_sansa_prediction_probabilities",
        ),
    )


def downgrade() -> None:
    op.drop_table("sansa_prediction_results")
