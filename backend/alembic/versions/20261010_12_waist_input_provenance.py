"""Preserve participant-entered waist value and unit."""
from alembic import op
import sqlalchemy as sa

revision = "20261010_12"
down_revision = "20261009_11"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("bia_records", sa.Column("waist_input_value", sa.DECIMAL(7, 2), nullable=True))
    op.add_column("bia_records", sa.Column("waist_input_unit", sa.String(10), nullable=True))


def downgrade():
    op.drop_column("bia_records", "waist_input_unit")
    op.drop_column("bia_records", "waist_input_value")
