"""Public, read-only research instrument definitions."""

from fastapi import APIRouter

from app.services.sansa_definition import public_definition


router = APIRouter(prefix="/sansa", tags=["instruments"])


@router.get("/definition")
def get_sansa_definition():
    """Return the canonical approved definition used by scoring and the form."""
    return public_definition()
