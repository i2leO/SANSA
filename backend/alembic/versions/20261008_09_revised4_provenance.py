"""Allow unknown visit dates and record revised4 score-only provenance."""
from alembic import op
import sqlalchemy as sa

revision = "20261008_09"
down_revision = "20261008_08"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("visits", "visit_date", existing_type=sa.Date(), nullable=True)
    op.add_column("sansa_responses", sa.Column("source_dataset", sa.String(100), nullable=True))
    op.add_column("sansa_responses", sa.Column("answer_capture_mode", sa.String(30), nullable=True))


def downgrade():
    op.drop_column("sansa_responses", "answer_capture_mode")
    op.drop_column("sansa_responses", "source_dataset")
    op.alter_column("visits", "visit_date", existing_type=sa.Date(), nullable=False)
