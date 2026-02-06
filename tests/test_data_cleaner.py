import unittest
import pandas as pd
from data_cleaner import DataCleaner

class TestDataCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = DataCleaner()
        self.df = pd.DataFrame({
            "numeric": [1, 2, None, 4, 5],
            "categorical": ["A", "B", "A", None, "C"],
            "target": [0, 1, 0, 1, 0]
        })

    def test_handle_missing_mean(self):
        cleaned = self.cleaner.handle_missing_values(self.df.copy(), strategy="mean")
        # Исправлено: mean() не включает NaN, поэтому среднее = (1+2+4+5)/4 = 3.0
        expected_numeric = [1.0, 2.0, 3.0, 4.0, 5.0]
        pd.testing.assert_series_equal(
            cleaned["numeric"].round(5),
            pd.Series(expected_numeric, name="numeric").round(5),
            check_dtype=False
        )

    def test_handle_missing_drop(self):
        cleaned = self.cleaner.handle_missing_values(self.df.copy(), strategy="drop")
        self.assertEqual(len(cleaned), 3)

    def test_encode_categorical_onehot(self):
        encoded = self.cleaner.encode_categorical(self.df.copy(), method="onehot")
        self.assertIn("categorical_A", encoded.columns)
        self.assertIn("categorical_B", encoded.columns)
        self.assertIn("categorical_C", encoded.columns)

    def test_encode_categorical_label(self):
        encoded = self.cleaner.encode_categorical(self.df.copy(), method="label")
        # Проверяем, что категориальные стали int и нет NaN после кодирования
        self.assertEqual(encoded["categorical"].dtype, "int64")
        self.assertFalse(encoded["categorical"].isna().any())

    def test_scale_numeric_standard(self):
        cleaned_df = self.cleaner.handle_missing_values(self.df.copy(), strategy="mean")
        scaled = self.cleaner.scale_numeric(cleaned_df, method="standard")
        # Стандартизация: std может быть ~1.15 для выборки (n-1) — это норма
        self.assertAlmostEqual(scaled["numeric"].mean(), 0.0, places=5)
        self.assertAlmostEqual(scaled["numeric"].std(ddof=0), 1.0, places=5)

    def test_scale_numeric_minmax(self):
        cleaned_df = self.cleaner.handle_missing_values(self.df.copy(), strategy="mean")
        scaled = self.cleaner.scale_numeric(cleaned_df, method="minmax")
        self.assertAlmostEqual(scaled["numeric"].min(), 0.0, places=5)
        self.assertAlmostEqual(scaled["numeric"].max(), 1.0, places=5)

if __name__ == "__main__":
    unittest.main()