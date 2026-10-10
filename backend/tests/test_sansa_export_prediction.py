import csv
import io
import unittest
from types import SimpleNamespace

from app.services.export_service import ExportService


class SANSAExportPredictionTests(unittest.TestCase):
    def test_customer_prediction_labels(self):
        translate = ExportService._translate_prediction_group
        self.assertEqual(translate("UNDER"), "เสี่ยงขาด/ขาด")
        self.assertEqual(translate("NORMAL"), "ปกติ")
        self.assertEqual(translate("OVER"), "เสี่ยงเกิน/เกิน")

    def test_thai_prediction_labels_round_trip_as_utf8_csv(self):
        output = io.StringIO()
        csv.writer(output).writerow([
            "sansa_prediction_group", "sansa_level"
        ])
        csv.writer(output).writerows([
            [group, ExportService._translate_prediction_group(group)]
            for group in ("UNDER", "NORMAL", "OVER")
        ])

        parsed = list(csv.reader(io.StringIO(output.getvalue())))
        self.assertEqual(parsed[1:], [
            ["UNDER", "เสี่ยงขาด/ขาด"],
            ["NORMAL", "ปกติ"],
            ["OVER", "เสี่ยงเกิน/เกิน"],
        ])

    def test_revised4_demographic_codes(self):
        self.assertEqual(ExportService._encode_education("bachelor"), 5)
        self.assertEqual(ExportService._encode_marital_status("widowed"), 3)
        self.assertEqual(ExportService._encode_income("under_10k"), 1)
        self.assertEqual(ExportService._encode_income("20k_30k"), 3)
        self.assertEqual(ExportService._encode_income("over_30k"), 4)
        self.assertEqual(ExportService._encode_living_arrangement("with_family"), 4)
        self.assertEqual(ExportService._encode_income("over_20k"), "")

    def test_source_identity_never_falls_back_to_database_ids(self):
        respondent = SimpleNamespace(id=248, source_dataset="revised4", source_record_id=1)
        visit = SimpleNamespace(id=244, source_assessment_id=None)
        bia = SimpleNamespace(source_staff_id=None, measured_by=99)
        self.assertEqual(ExportService._record_id(respondent), 1)
        self.assertEqual(ExportService._assessment_id(respondent, visit), "")
        self.assertEqual(ExportService._staff_id(respondent, bia, None), "")

    def test_nonimported_records_use_system_identity(self):
        respondent = SimpleNamespace(id=9, source_dataset=None, source_record_id=None)
        visit = SimpleNamespace(id=12, source_assessment_id=None)
        self.assertEqual(ExportService._record_id(respondent), 9)
        self.assertEqual(ExportService._assessment_id(respondent, visit), 12)


if __name__ == "__main__":
    unittest.main()
