import unittest
import pandas as pd
import numpy as np
from data_analyze import DataAnalyzer

class TestDataAnalyzer(unittest.TestCase):
    def setUp(self):
        # Увеличиваем размер данных, чтобы stratify работал с test_size=0.2
        self.df = pd.DataFrame({
            "age": [25, 30, 35, 40, 45, 50, 55, 60],
            "salary": [50000, 60000, 70000, 80000, 55000, 65000, 75000, 85000],
            "category": ["A", "B", "A", "B", "A", "B", "A", "B"]  # Теперь по 4 элемента на класс
        })
        self.analyzer = DataAnalyzer(self.df)

    def test_basic_statistics(self):
        try:
            self.analyzer.basic_statistics()
        except Exception as e:
            self.fail(f"basic_statistics() вызвала ошибку: {e}")

    def test_find_anomalies(self):
        try:
            self.analyzer.find_anomalies(z_thresh=2.0)
        except Exception as e:
            self.fail(f"find_anomalies() вызвала ошибку: {e}")

    def test_build_regression_model_linear(self):
        try:
            self.analyzer.build_regression_model("salary", model_type="linear")
        except Exception as e:
            self.fail(f"build_regression_model(linear) вызвала ошибку: {e}")

    def test_build_classification_model_logistic(self):
        try:
            self.analyzer.build_classification_model("category", model_type="logistic")
        except Exception as e:
            self.fail(f"build_classification_model(logistic) вызвала ошибку: {e}")

if __name__ == "__main__":
    unittest.main()