"""Add revocable QR credentials for staff and admin accounts."""
from alembic import op
import sqlalchemy as sa

revision = "20261002_06"
down_revision = "20261002_05"
branch_labels = None
depends_on = None


def _columns():
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}


def upgrade() -> None:
    if "qr_secret_hash" not in _columns():
        op.add_column("users", sa.Column("qr_secret_hash", sa.String(64), nullable=True))
        op.create_unique_constraint("uq_users_qr_secret_hash", "users", ["qr_secret_hash"])


def downgrade() -> None:
    if "qr_secret_hash" in _columns():
        op.drop_constraint("uq_users_qr_secret_hash", "users", type_="unique")
        op.drop_column("users", "qr_secret_hash")
