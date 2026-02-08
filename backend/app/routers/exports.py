from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.models import User
from app.services.export_service import ExportService
from app.auth import get_current_staff_or_admin

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/sansa.csv")
def export_sansa(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    facility_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Export SANSA data to CSV (SPSS format)"""
    export_service = ExportService(db)
    csv_content = export_service.export_sansa_csv(start_date, end_date, facility_id)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=sansa_export_{date.today().isoformat()}.csv"
        },
    )


@router.get("/mna.csv")
def export_mna(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Export MNA data to CSV (SPSS format)"""
    export_service = ExportService(db)
    csv_content = export_service.export_mna_csv(start_date, end_date)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=mna_export_{date.today().isoformat()}.csv"
        },
    )


@router.get("/bia.csv")
def export_bia(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Export BIA/anthropometry data to CSV (SPSS format)"""
    export_service = ExportService(db)
    csv_content = export_service.export_bia_csv(start_date, end_date)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=bia_export_{date.today().isoformat()}.csv"
        },
    )


@router.get("/satisfaction.csv")
def export_satisfaction(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Export Satisfaction survey data to CSV (SPSS format)"""
    export_service = ExportService(db)
    csv_content = export_service.export_satisfaction_csv(start_date, end_date)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=satisfaction_export_{date.today().isoformat()}.csv"
        },
    )


@router.get("/combined.csv")
def export_combined(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Export combined dataset with all instruments"""
    export_service = ExportService(db)
    csv_content = export_service.export_combined_csv(start_date, end_date)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=combined_export_{date.today().isoformat()}.csv"
        },
    )
