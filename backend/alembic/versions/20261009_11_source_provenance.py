"""Add stable workbook identity and import provenance."""
from alembic import op
import sqlalchemy as sa

revision = "20261009_11"
down_revision = "20261009_10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "source_import_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_dataset", sa.String(100), nullable=False),
        sa.Column("source_filename", sa.String(255), nullable=False),
        sa.Column("source_sha256", sa.String(64), nullable=False),
        sa.Column("schema_version", sa.String(100), nullable=False),
        sa.Column("populated_rows", sa.Integer(), nullable=False),
        sa.Column("sheet_manifest", sa.JSON(), nullable=False),
        sa.Column("imported_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_sha256", name="uq_source_import_sha256"),
    )
    op.create_index("ix_source_import_batches_source_dataset", "source_import_batches", ["source_dataset"])
    op.create_index("ix_source_import_batches_source_sha256", "source_import_batches", ["source_sha256"])
    op.create_table(
        "source_import_sheets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("import_batch_id", sa.Integer(), nullable=False),
        sa.Column("sheet_name", sa.String(100), nullable=False),
        sa.Column("sheet_role", sa.String(30), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("column_count", sa.Integer(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("values_json", sa.JSON(), nullable=False),
        sa.Column("formulas_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["source_import_batches.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("import_batch_id", "sheet_name", name="uq_source_import_sheet"),
    )
    op.create_index("ix_source_import_sheets_import_batch_id", "source_import_sheets", ["import_batch_id"])
    op.add_column("respondents", sa.Column("source_dataset", sa.String(100), nullable=True))
    op.add_column("respondents", sa.Column("source_record_id", sa.Integer(), nullable=True))
    op.add_column("respondents", sa.Column("source_import_batch_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_respondents_source_import_batch", "respondents", "source_import_batches",
        ["source_import_batch_id"], ["id"],
    )
    op.create_unique_constraint(
        "uq_respondent_source_record", "respondents", ["source_dataset", "source_record_id"]
    )
    op.create_index("ix_respondents_source_dataset", "respondents", ["source_dataset"])
    op.create_index("ix_respondents_source_import_batch_id", "respondents", ["source_import_batch_id"])
    op.add_column("visits", sa.Column("source_assessment_id", sa.String(100), nullable=True))
    op.create_index("ix_visits_source_assessment_id", "visits", ["source_assessment_id"])
    op.add_column("bia_records", sa.Column("source_staff_id", sa.String(100), nullable=True))


def downgrade():
    op.drop_column("bia_records", "source_staff_id")
    op.drop_index("ix_visits_source_assessment_id", table_name="visits")
    op.drop_column("visits", "source_assessment_id")
    op.drop_index("ix_respondents_source_import_batch_id", table_name="respondents")
    op.drop_index("ix_respondents_source_dataset", table_name="respondents")
    op.drop_constraint("uq_respondent_source_record", "respondents", type_="unique")
    op.drop_constraint("fk_respondents_source_import_batch", "respondents", type_="foreignkey")
    op.drop_column("respondents", "source_import_batch_id")
    op.drop_column("respondents", "source_record_id")
    op.drop_column("respondents", "source_dataset")
    op.drop_table("source_import_sheets")
    op.drop_table("source_import_batches")
