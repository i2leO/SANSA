"""Allow a third account role without changing existing users."""
from alembic import op
import sqlalchemy as sa

revision = '20260915_03'
down_revision = '20260913_02'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'users', 'role',
        existing_type=sa.Enum('ADMIN', 'STAFF', name='userrole'),
        type_=sa.Enum('ADMIN', 'STAFF', 'USER', name='userrole'),
        existing_nullable=False,
    )


def downgrade():
    connection = op.get_bind()
    if connection.execute(sa.text("SELECT COUNT(*) FROM users WHERE role = 'USER'")).scalar():
        raise RuntimeError('Cannot downgrade while USER accounts exist')
    op.alter_column(
        'users', 'role',
        existing_type=sa.Enum('ADMIN', 'STAFF', 'USER', name='userrole'),
        type_=sa.Enum('ADMIN', 'STAFF', name='userrole'),
        existing_nullable=False,
    )
