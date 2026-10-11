"""Preserve longitudinal MNA/BIA revisions under the same respondent."""
from alembic import op
import sqlalchemy as sa

revision = "20261009_10"
down_revision = "20261008_09"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    duplicates = connection.execute(sa.text(
        "SELECT visit_id FROM bia_records GROUP BY visit_id HAVING COUNT(*) > 1 LIMIT 1"
    )).first()
    if duplicates:
        raise RuntimeError("duplicate BIA rows must be resolved before enabling one BIA per assessment occurrence")
    op.create_unique_constraint("uq_bia_visit", "bia_records", ["visit_id"])
    op.create_table(
        "assessment_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("respondent_id", sa.Integer(), nullable=False),
        sa.Column("visit_id", sa.Integer(), nullable=False),
        sa.Column("instrument", sa.String(20), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(20), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("change_reason", sa.String(255), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("recorded_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["respondent_id"], ["respondents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.UniqueConstraint("instrument", "record_id", "revision_number", name="uq_assessment_revision"),
    )
    op.create_index("ix_assessment_revisions_respondent_id", "assessment_revisions", ["respondent_id"])
    op.create_index("ix_assessment_revisions_visit_id", "assessment_revisions", ["visit_id"])
    op.create_index("ix_assessment_revisions_instrument", "assessment_revisions", ["instrument"])
    op.create_index("ix_assessment_revisions_record_id", "assessment_revisions", ["record_id"])
    op.create_index("ix_assessment_revisions_changed_by", "assessment_revisions", ["changed_by"])
    op.create_index("ix_assessment_revisions_is_current", "assessment_revisions", ["is_current"])
    op.create_index("ix_assessment_revisions_recorded_at", "assessment_revisions", ["recorded_at"])
    op.create_index("idx_assessment_history", "assessment_revisions", ["respondent_id", "instrument", "recorded_at"])


def downgrade():
    op.drop_table("assessment_revisions")
    op.drop_constraint("uq_bia_visit", "bia_records", type_="unique")
