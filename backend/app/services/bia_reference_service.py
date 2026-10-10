"""Revised4 reference rules; never modify stored BIA measurements."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def _number(value, name):
    if value is None or isinstance(value, bool):
        raise ValueError(f"Missing or invalid {name}")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid {name}") from None
    if not number.is_finite():
        raise ValueError(f"Invalid {name}")
    return number


def _rounded(value, name):
    try:
        return _number(value, name).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError(f"Invalid {name}") from None


def classify_bmi_glim(age, bmi):
    age = _number(age, "age")
    bmi = _rounded(bmi, "BMI")
    cutoff = Decimal("18.5") if age < 70 else Decimal("20")
    return "UNDER" if bmi < cutoff else "OVER" if bmi >= 25 else "NORMAL"


def classify_body_fat(sex, pbf):
    sex = getattr(sex, "value", sex)
    if sex not in ("male", "female"):
        raise ValueError("Unsupported sex for PBF classification")
    pbf = _rounded(pbf, "PBF")  # Excel revised4 rounds both BMI and PBF.
    lower, upper = (15, 25) if sex == "male" else (20, 35)
    return "UNDER" if pbf < lower else "OVER" if pbf > upper else "NORMAL"


def derive_nutrition_reference(age, sex, bmi, pbf):
    bmi_class = classify_bmi_glim(age, bmi)
    pbf_class = classify_body_fat(sex, pbf)
    classes = (bmi_class, pbf_class)
    reference = "UNDER" if "UNDER" in classes else "OVER" if "OVER" in classes else "NORMAL"
    return {"bmi_rounded": _rounded(bmi, "BMI"), "bmi_class": bmi_class,
            "pbf_class": pbf_class, "nutrition_reference": reference}
