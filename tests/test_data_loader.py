import unittest
import pandas as pd
import os
from data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаём тестовые файлы
        cls.csv_file = "test_data.csv"
        cls.xlsx_file = "test_data.xlsx"

        df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": ["x", "y", "z"]
        })
        df.to_csv(cls.csv_file, index=False)
        df.to_excel(cls.xlsx_file, index=False)

    @classmethod
    def tearDownClass(cls):
        # Удаляем тестовые файлы
        if os.path.exists(cls.csv_file):
            os.remove(cls.csv_file)
        if os.path.exists(cls.xlsx_file):
            os.remove(cls.xlsx_file)

    def setUp(self):
        self.loader = DataLoader()

    def test_load_csv(self):
        df = self.loader.load_csv(self.csv_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn("A", df.columns)

    def test_load_excel(self):
        df = self.loader.load_excel(self.xlsx_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)

    def test_load_excel_sheet(self):
        # Сохраняем с двумя листами
        with pd.ExcelWriter(self.xlsx_file) as writer:
            pd.DataFrame({"X": [1]}).to_excel(writer, sheet_name="Sheet1", index=False)
            pd.DataFrame({"Y": [2]}).to_excel(writer, sheet_name="Data", index=False)

        df = self.loader.load_excel(self.xlsx_file, sheet_name="Data")
        self.assertEqual(len(df.columns), 1)
        self.assertIn("Y", df.columns)

    def test_load_from_api_json(self):
        # Тест с моком будет в расширенной версии
        pass  # Заглушка для примера

if __name__ == "__main__":
    unittest.main()