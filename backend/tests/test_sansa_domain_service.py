"""Focused pure-function checks; synthetic records, no database connection."""

import unittest
from decimal import Decimal
from types import SimpleNamespace

from app.services.sansa_domain_service import age_group01, calculate_sansa_domain_scores


class SANSADomainTests(unittest.TestCase):
    def response(self, **overrides):
        fields = {f"q{i}_score": Decimal("0") for i in range(1, 17)}
        fields.update(overrides)
        return SimpleNamespace(**fields)

    def test_d1(self):
        response = self.response(q1_score=99, q5_score=1, q6_score=2, q7_score=4)
        before = vars(response).copy()
        self.assertEqual(calculate_sansa_domain_scores(response), {
            "d1_total": Decimal("7"), "d2_total": Decimal("0"),
            "d3_total": Decimal("0"),
        })
        self.assertEqual(vars(response), before)

    def test_d2(self):
        response = self.response(q8_score=1, q9_score=2, q10_score=3,
                                 q11_score=4, q12_score=0, q13_score=2)
        self.assertEqual(calculate_sansa_domain_scores(response), {
            "d1_total": Decimal("0"), "d2_total": Decimal("12"),
            "d3_total": Decimal("0"),
        })

    def test_d3(self):
        response = self.response(q14_score=Decimal("0.1"),
                                 q15_score=Decimal("0.2"), q16_score=4)
        self.assertEqual(calculate_sansa_domain_scores(response), {
            "d1_total": Decimal("0"), "d2_total": Decimal("0"),
            "d3_total": Decimal("4.3"),
        })

    def test_missing_score_is_not_zero(self):
        with self.assertRaisesRegex(ValueError, "q8_score"):
            calculate_sansa_domain_scores(self.response(q8_score=None))

    def test_age_under_70(self):
        self.assertEqual(age_group01(SimpleNamespace(age=69)), 0)

    def test_age_70_or_above(self):
        for age in (70, 85):
            with self.subTest(age=age):
                self.assertEqual(age_group01(SimpleNamespace(age=age)), 1)

    def test_missing_age(self):
        with self.assertRaisesRegex(ValueError, "Missing respondent age"):
            age_group01(SimpleNamespace(age=None))
