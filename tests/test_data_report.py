import unittest
import os
import pandas as pd  # 🔽 Исправлено: добавлен импорт pandas
from data_report import DataReport

class TestDataReport(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": [4.0, 5.0, 6.0]
        })
        self.report = DataReport(self.df, report_name="test_report")
        self.out_dir = "test_reports"
        os.makedirs(self.out_dir, exist_ok=True)

    def test_generate_key_metrics(self):
        metrics = self.report.generate_key_metrics()
        self.assertIn("rows", metrics)
        self.assertEqual(metrics["rows"], 3)

    def test_export_pdf(self):
        pdf_path = self.report.export_pdf(os.path.join(self.out_dir, "test.pdf"))
        self.assertTrue(os.path.exists(pdf_path))

    def test_export_excel(self):
        xlsx_path = self.report.export_excel(os.path.join(self.out_dir, "test.xlsx"))
        self.assertTrue(os.path.exists(xlsx_path))

    def test_save_matplotlib_plots(self):
        paths = self.report.save_matplotlib_seaborn_plots(os.path.join(self.out_dir, "figures"))
        self.assertGreater(len(paths), 0)
        for path in paths.values():
            self.assertTrue(os.path.exists(path))

    def test_save_plotly_interactive(self):
        paths = self.report.save_plotly_interactive(os.path.join(self.out_dir, "interactive"))
        self.assertGreater(len(paths), 0)
        for path in paths.values():
            self.assertTrue(os.path.exists(path))

    def tearDown(self):
        # Очистка после тестов
        import shutil
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)

if __name__ == "__main__":
    unittest.main()