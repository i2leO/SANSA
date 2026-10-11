"""Register the approved SANSA 0/2/4 definition without rescoring history.

Revision ID: 20261008_08
Revises: 20261004_07
"""

from datetime import date

from alembic import op
import sqlalchemy as sa


revision = "20261008_08"
down_revision = "20261004_07"
branch_labels = None
depends_on = None

VERSION = "0.2.4-20261008"


def upgrade() -> None:
    bind = op.get_bind()
    existing = bind.execute(
        sa.text(
            "SELECT id FROM scoring_rule_versions "
            "WHERE instrument_name = :instrument AND version_number = :version"
        ),
        {"instrument": "SANSA", "version": VERSION},
    ).scalar()

    bind.execute(
        sa.text(
            "UPDATE scoring_rule_versions SET is_active = :inactive "
            "WHERE instrument_name = :instrument"
        ),
        {"inactive": False, "instrument": "SANSA"},
    )

    if existing is None:
        bind.execute(
            sa.text(
                "INSERT INTO scoring_rule_versions "
                "(instrument_name, version_number, version_name, description, is_active, effective_date) "
                "VALUES (:instrument, :version, :name, :description, :active, :effective_date)"
            ),
            {
                "instrument": "SANSA",
                "version": VERSION,
                "name": "SANSA approved 0/2/4",
                "description": (
                    "Executable item mapping: SANSA_0_2_4_PDF_2026-10-08; "
                    "PDF pages 5-9; revised4 observations/model use the 0/2/4 scale"
                ),
                "active": True,
                "effective_date": date(2026, 10, 8),
            },
        )
    else:
        bind.execute(
            sa.text("UPDATE scoring_rule_versions SET is_active = :active WHERE id = :id"),
            {"active": True, "id": existing},
        )


def downgrade() -> None:
    # Never delete a provenance row: responses may reference it. Downgrade only
    # disables this version; reactivation of an older version is an owner action.
    op.get_bind().execute(
        sa.text(
            "UPDATE scoring_rule_versions SET is_active = :inactive "
            "WHERE instrument_name = :instrument AND version_number = :version"
        ),
        {"inactive": False, "instrument": "SANSA", "version": VERSION},
    )
