import unittest
from decimal import Decimal
from app.services.bia_reference_service import classify_bmi_glim, classify_body_fat, derive_nutrition_reference


class BIAReferenceTests(unittest.TestCase):
    def test_bmi_boundaries(self):
        values = (18.4, 18.5, 19.9, 20, 24.9, 25)
        for age, expected in ((69, ("UNDER", "NORMAL", "NORMAL", "NORMAL", "NORMAL", "OVER")),
                              (70, ("UNDER", "UNDER", "UNDER", "NORMAL", "NORMAL", "OVER"))):
            for bmi, group in zip(values, expected):
                with self.subTest(age=age, bmi=bmi):
                    self.assertEqual(classify_bmi_glim(age, bmi), group)

    def test_pbf_boundaries(self):
        for sex, values in (("male", (14.9, 15, 25, 25.1)), ("female", (19.9, 20, 35, 35.1))):
            for pbf, group in zip(values, ("UNDER", "NORMAL", "NORMAL", "OVER")):
                with self.subTest(sex=sex, pbf=pbf):
                    self.assertEqual(classify_body_fat(sex, pbf), group)

    def test_excel_rounding(self):
        self.assertEqual(classify_bmi_glim(69, Decimal("18.45")), "NORMAL")
        self.assertEqual(classify_bmi_glim(70, Decimal("19.95")), "NORMAL")
        self.assertEqual(classify_bmi_glim(69, Decimal("24.95")), "OVER")
        self.assertEqual(classify_body_fat("male", Decimal("25.04")), "NORMAL")
        self.assertEqual(classify_body_fat("male", Decimal("25.05")), "OVER")

    def test_priority(self):
        for bmi, pbf, expected in ((18, 30, "UNDER"), (26, 14, "UNDER"), (26, 20, "OVER"), (22, 20, "NORMAL")):
            self.assertEqual(derive_nutrition_reference(69, "male", bmi, pbf)["nutrition_reference"], expected)

    def test_unsupported_or_missing(self):
        for sex in (None, "other", "prefer_not_to_say", 1):
            with self.subTest(sex=sex), self.assertRaises(ValueError):
                classify_body_fat(sex, 20)
        for value in (None, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                classify_bmi_glim(69, value)
