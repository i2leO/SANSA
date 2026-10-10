"""Revocable respondent QR credentials."""
from alembic import op
import sqlalchemy as sa
revision = '20260913_02'
down_revision = '20260912_01'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('respondents', sa.Column('qr_secret_hash', sa.String(64), nullable=True))
    op.create_index('uq_respondents_qr_secret_hash', 'respondents', ['qr_secret_hash'], unique=True)

def downgrade():
    op.drop_index('uq_respondents_qr_secret_hash', table_name='respondents')
    op.drop_column('respondents', 'qr_secret_hash')
