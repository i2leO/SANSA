"""Distinguish score-only MNA imports from recorded raw answers."""
from alembic import op
import sqlalchemy as sa

revision = "20261010_13"
down_revision = "20261010_12"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("mna_responses", sa.Column("source_dataset", sa.String(50), nullable=False, server_default="web"))
    op.add_column("mna_responses", sa.Column("answer_capture_mode", sa.String(30), nullable=False, server_default="raw_answers"))


def downgrade():
    op.drop_column("mna_responses", "answer_capture_mode")
    op.drop_column("mna_responses", "source_dataset")
