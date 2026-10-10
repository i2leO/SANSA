"""Add media metadata to existing knowledge posts."""
from alembic import op
import sqlalchemy as sa

revision = "20260928_04"
down_revision = "20260915_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("knowledge_posts", sa.Column("media_path", sa.String(500), nullable=True))
    op.add_column("knowledge_posts", sa.Column("media_type", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("knowledge_posts", "media_type")
    op.drop_column("knowledge_posts", "media_path")
