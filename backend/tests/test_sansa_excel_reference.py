"""Compare cached revised4 reference outputs without importing participant data."""
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import unittest
from app.services.sansa_domain_service import calculate_sansa_domain_scores, age_group01
from app.services.sansa_prediction_service import predict_sansa_nutrition_status
from app.services.bia_reference_service import derive_nutrition_reference

BOOK = Path(__file__).resolve().parents[2] / 'Use SANSA Integrated WebApp Data (revised4).xlsx'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

@unittest.skipUnless(BOOK.exists(), 'Local revised4 reference workbook unavailable')
class ExcelReferenceTests(unittest.TestCase):
    def test_200_reference_cases(self):
        with ZipFile(BOOK) as z:
            strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
            def sheet(index):
                rows = []
                for row in ET.fromstring(z.read(f'xl/worksheets/sheet{index}.xml')).find('m:sheetData', NS):
                    values = {}
                    for c in row:
                        v = c.findtext('m:v', '', NS)
                        values[''.join(filter(str.isalpha, c.attrib['r']))] = strings[int(v)] if c.attrib.get('t') == 's' and v else v
                    rows.append(values)
                return rows
            participants, predictions, bia = sheet(1), sheet(2), sheet(3)
        categories = {'ขาด/เสี่ยงขาด': 'UNDER', 'ปกติ': 'NORMAL', 'เสี่ยงเกิน/เกิน': 'OVER',
                      'Under':'UNDER','Normal':'NORMAL','Over':'OVER','UNDER':'UNDER','NORMAL':'NORMAL','OVER':'OVER'}
        count = 0
        for row, (p, pred, b) in enumerate(zip(participants[1:], predictions[1:], bia[1:]), 2):
            if not p.get('E'): continue
            count += 1
            with self.subTest(excel_row=row):
                domains = calculate_sansa_domain_scores(SimpleNamespace(**{f'q{i}_score':p[col] for i,col in enumerate(['AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM'],5)}))
                for key, col in zip(domains, ['AN','AO','AP']):
                    self.assertAlmostEqual(float(domains[key]), float(p[col]), places=10)
                group = age_group01(SimpleNamespace(age=float(p['E'])))
                self.assertEqual(group, int(float(pred['D'])))
                self.assertAlmostEqual(float(p['AS']), float(pred['G']), places=10)
                result = predict_sansa_nutrition_status(domains['d2_total'], domains['d3_total'], float(p['AS']), group)
                for key,col in [('l_over','H'),('l_normal','I'),('p_under','M'),('p_over','N'),('p_normal','O')]:
                    self.assertAlmostEqual(float(result[key]),float(pred[col]),places=10,msg=key)
                self.assertEqual(result['predicted_group'],categories[pred['P']])
                sex = {'ชาย':'male','หญิง':'female','1':'male','2':'female','male':'male','female':'female'}[p['G']]
                ref = derive_nutrition_reference(float(p['E']),sex,b['G'],b['I'])
                for key,col in [('bmi_class','AN'),('pbf_class','AO'),('nutrition_reference','AP')]:
                    self.assertEqual(ref[key], categories[b[col]],key)
        self.assertEqual(count,200)
