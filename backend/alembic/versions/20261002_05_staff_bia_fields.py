"""Add staff BIA measurements when absent from the deployed schema."""
from alembic import op
import sqlalchemy as sa

revision = "20261002_05"
down_revision = "20260928_04"
branch_labels = None
depends_on = None


def _columns():
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns("bia_records")}


def upgrade() -> None:
    existing = _columns()
    additions = {
        "visceral_fat_level": sa.Column("visceral_fat_level", sa.DECIMAL(5, 2), nullable=True),
        "mac_cm": sa.Column("mac_cm", sa.DECIMAL(5, 2), nullable=True),
        "cc_cm": sa.Column("cc_cm", sa.DECIMAL(5, 2), nullable=True),
    }
    for name, column in additions.items():
        if name not in existing:
            op.add_column("bia_records", column)


def downgrade() -> None:
    existing = _columns()
    for name in ("cc_cm", "mac_cm", "visceral_fat_level"):
        if name in existing:
            op.drop_column("bia_records", name)
