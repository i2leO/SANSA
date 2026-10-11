"""Expose existing research MNA fields, adding only absent nullable columns.

No backfill or score recalculation. Downgrade retains research observations:
these columns may predate this revision in databases imported from the SQL dump.
"""
from alembic import op
import sqlalchemy as sa

revision = "20261004_07"
down_revision = "20261002_06"
branch_labels = None
depends_on = None


def upgrade():
    existing = {column['name'] for column in sa.inspect(op.get_bind()).get_columns('mna_responses')}
    for name, kind in [
        ('q19_calf_circumference_assess', sa.String(50)),
        ('mna_a12', sa.DECIMAL(10, 2)),
        ('mac_cm', sa.DECIMAL(5, 2)),
        ('cc_cm', sa.DECIMAL(5, 2)),
    ]:
        if name not in existing:
            op.add_column('mna_responses', sa.Column(name, kind, nullable=True))


def downgrade():
    # Retain columns and their data intentionally; older application code ignores them.
    pass
