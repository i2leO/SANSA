"""Focused CSV download encoding check with synthetic text only."""

import csv
import io
import unittest

from app.routers.exports import csv_download


class CSVEncodingTests(unittest.TestCase):
    def test_excel_utf8_marker_preserves_thai_cells_and_columns(self):
        source = 'sansa_level,score\r\n"เสี่ยงขาด",27\r\n'
        response = csv_download(source, "sansa_export.csv")
        self.assertTrue(response.body.startswith(b"\xef\xbb\xbf"))
        self.assertIn("charset=utf-8", response.headers["content-type"])
        self.assertEqual(response.headers["content-disposition"],
                         "attachment; filename=sansa_export.csv")
        parsed = list(csv.reader(io.StringIO(response.body.decode("utf-8-sig"))))
        self.assertEqual(parsed, [["sansa_level", "score"], ["เสี่ยงขาด", "27"]])


if __name__ == "__main__":
    unittest.main()
