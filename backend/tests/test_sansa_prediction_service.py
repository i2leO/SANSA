import math
import unittest
from decimal import Decimal
from types import SimpleNamespace

from app.services.sansa_domain_service import age_group01, calculate_sansa_domain_scores
from app.services.sansa_prediction_service import predict_sansa_nutrition_status


class PredictionTests(unittest.TestCase):
    def test_task2_inputs_and_known_logits(self):
        response = SimpleNamespace(**{f"q{i}_score": Decimal("1") for i in range(5, 17)})
        scores = calculate_sansa_domain_scores(response)
        result = predict_sansa_nutrition_status(
            scores["d2_total"], scores["d3_total"], Decimal("80"),
            age_group01(SimpleNamespace(age=69)),
        )
        self.assertEqual(len(result), 10)
        self.assertAlmostEqual(result["l_over"], 3.278)
        self.assertAlmostEqual(result["l_normal"], 4.178)
        denominator = 1 + math.exp(3.278) + math.exp(4.178)
        self.assertAlmostEqual(result["p_under"], 1 / denominator)
        self.assertAlmostEqual(result["p_over"], math.exp(3.278) / denominator)
        self.assertAlmostEqual(result["p_normal"], math.exp(4.178) / denominator)
        self.assertEqual(result["predicted_group"], "NORMAL")

    def test_probability_sum_maximum_and_boundaries(self):
        groups = set()
        for waist in (0, 40, 60, 80, 100, 250, 10000):
            for age in (0, 1):
                with self.subTest(waist=waist, age=age):
                    result = predict_sansa_nutrition_status(0, 0, waist, age)
                    probs = {g: result[f"p_{g.lower()}"] for g in ("UNDER", "OVER", "NORMAL")}
                    self.assertAlmostEqual(sum(probs.values()), 1, places=14)
                    self.assertTrue(all(math.isfinite(p) and 0 <= p <= 1 for p in probs.values()))
                    self.assertEqual(probs[result["predicted_group"]], max(probs.values()))
                    groups.add(result["predicted_group"])
        self.assertEqual(groups, {"UNDER", "NORMAL", "OVER"})

    def test_age_coefficients(self):
        younger = predict_sansa_nutrition_status(12, 6, 85, 0)
        older = predict_sansa_nutrition_status(12, 6, 85, 1)
        self.assertAlmostEqual(older["l_over"] - younger["l_over"], -2.336)
        self.assertAlmostEqual(older["l_normal"] - younger["l_normal"], -2.489)

    def test_invalid_numeric_inputs(self):
        for value in (None, float("nan"), float("inf"), "80", True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                predict_sansa_nutrition_status(12, 6, value, 0)
        with self.assertRaises(ValueError):
            predict_sansa_nutrition_status(12, 6, 80, 2)
