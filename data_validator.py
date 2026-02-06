import pandas as pd
import numpy as np
from scipy import stats


class DataValidator:
    @staticmethod
    def validate_data(df):
        if not isinstance(df, pd.DataFrame):
            print("[WARNING] Переданные данные не являются DataFrame.")
            return

        print("\n[VALIDATION] Начало валидации данных...\n")

        duplicates = df.duplicated().sum()
        print(f"🔍 Дубликатов: {duplicates}")

        missing = df.isnull().sum()
        missing_total = missing.sum()
        if missing_total > 0:
            print(f"\n📉 Пропущенные значения:\n{missing[missing > 0]}")
        else:
            print("\n📉 Пропущенные значения: не обнаружены ✅")

        print(f"\n🧾 Типы данных:\n{df.dtypes}")

        num_cols = df.select_dtypes(include=[np.number])
        if not num_cols.empty:
            print("\n📊 Выбросы (по IQR и Z-оценке):")

            for col in num_cols.columns:
                col_data = num_cols[col].dropna()

                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                outliers_iqr = ((col_data < (Q1 - 1.5 * IQR)) | (col_data > (Q3 + 1.5 * IQR))).sum()

                z_scores = np.abs(stats.zscore(col_data))
                outliers_z = (z_scores > 3).sum()

                print(f" - {col}: выбросов по IQR = {outliers_iqr}, по Z-score = {outliers_z}")
        else:
            print("[INFO] Числовых столбцов не найдено для определения выбросов.")

        print("\n[VALIDATION] Валидация завершена.\n")