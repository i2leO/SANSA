"""Persist a Task 3 prediction without changing any source assessment."""

from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models import SANSAPredictionResult, Visit
from app.services.sansa_prediction_service import MODEL_VERSION, predict_sansa_nutrition_status


def save_sansa_prediction(
    db: Session, visit_id: int, *, d2_total, d3_total, waist_cm, age_group01
) -> SANSAPredictionResult:
    """Upsert this engine's version; caller owns commit/rollback.

    Lock the parent visit to serialize writers even before a prediction exists.
    Inputs are the Task 2 outputs and the caller's explicitly selected BIA waist.
    """
    prediction = predict_sansa_nutrition_status(d2_total, d3_total, waist_cm, age_group01)
    # Retain exact input decimals; reject extra storage precision instead of
    # silently changing the inputs used by the prediction engine.
    for name, original in (("d2_total", d2_total), ("d3_total", d3_total), ("waist_cm", waist_cm)):
        value = Decimal(str(original))
        if abs(value) >= Decimal("100000000") or value != value.quantize(Decimal("0.0001")):
            raise ValueError(f"{name} exceeds DECIMAL(12,4) storage precision")
        prediction[name] = value

    visit = db.query(Visit).filter(Visit.id == visit_id).with_for_update().first()
    if visit is None:
        raise ValueError("Visit not found")
    result = db.query(SANSAPredictionResult).filter(
        SANSAPredictionResult.visit_id == visit_id,
        SANSAPredictionResult.model_version == MODEL_VERSION,
    ).populate_existing().with_for_update().first()
    if result is None:
        result = SANSAPredictionResult(visit_id=visit_id, model_version=MODEL_VERSION)
        db.add(result)
    for field, value in prediction.items():
        if field not in ("age_group01", "predicted_group"):
            value = Decimal(str(value))
        setattr(result, field, value)
    result.updated_at = func.now()
    db.flush()
    db.refresh(result)
    return result
