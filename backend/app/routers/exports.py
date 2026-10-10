from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.models import User
from app.services.export_service import ExportService
from app.auth import get_current_staff_or_admin

router = APIRouter(prefix="/exports", tags=["exports"])


def csv_download(content: str, filename: str) -> Response:
    """Mark UTF-8 CSV for Excel without changing exported values or columns."""
    return Response(
        content=b"\xef\xbb\xbf" + content.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


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

    return csv_download(csv_content, f"sansa_export_{date.today().isoformat()}.csv")


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

    return csv_download(csv_content, f"mna_export_{date.today().isoformat()}.csv")


@router.get("/prediction.csv")
def export_prediction(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    export_service = ExportService(db)
    csv_content = export_service.export_prediction_csv(start_date, end_date)
    return csv_download(csv_content, f"prediction_export_{date.today().isoformat()}.csv")


@router.get("/revised4.xlsx")
def export_revised4_workbook(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    content = ExportService(db).export_revised4_xlsx(start_date, end_date)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
                f"attachment; filename=sansa_revised4_{date.today().isoformat()}.xlsx"
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

    return csv_download(csv_content, f"bia_export_{date.today().isoformat()}.csv")


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

    return csv_download(csv_content, f"satisfaction_export_{date.today().isoformat()}.csv")


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

    return csv_download(csv_content, f"combined_export_{date.today().isoformat()}.csv")


@router.get("/assessment-history.csv")
def export_assessment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Export every immutable MNA/BIA revision for longitudinal audit."""
    content = ExportService(db).export_assessment_history_csv()
    return csv_download(content, f"assessment_history_{date.today().isoformat()}.csv")
