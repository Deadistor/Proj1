import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler

class DataCleaner:
    def __init__(self):
        self.label_encoders = {}

    def handle_missing_values(self, df, strategy="mean"):
        df = df.copy()
        if strategy == "mean":
            df.fillna(df.mean(numeric_only=True), inplace=True)
        elif strategy == "median":
            df.fillna(df.median(numeric_only=True), inplace=True)
        elif strategy == "drop":
            df.dropna(inplace=True)
        else:
            print(f"[WARNING] Неизвестная стратегия: {strategy}")
        return df

    def drop_duplicates(self, df):
        before = df.shape[0]
        df = df.drop_duplicates()
        after = df.shape[0]
        print(f"[INFO] Удалено дубликатов: {before - after}")
        return df

    def encode_categorical(self, df, method="onehot"):
        df_encoded = df.copy()
        cat_cols = df_encoded.select_dtypes(include=["object", "category", "bool"]).columns

        if method == "label":
            le = LabelEncoder()
            for col in cat_cols:
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
        elif method == "onehot":
            df_encoded = pd.get_dummies(df_encoded, columns=cat_cols, drop_first=False)
            bool_cols = df_encoded.select_dtypes(include=["bool"]).columns
            df_encoded[bool_cols] = df_encoded[bool_cols].astype(int)
        else:
            raise ValueError("Метод кодирования должен быть 'label' или 'onehot'")
        return df_encoded

    def scale_numeric(self, df, method="standard"):
        df = df.copy()
        num_cols = df.select_dtypes(include=[np.number]).columns
        binary_cols = [col for col in num_cols if set(df[col].unique()) <= {0, 1}]
        scale_cols = [col for col in num_cols if col not in binary_cols]

        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        else:
            print(f"[WARNING] Неизвестный метод масштабирования: {method}")
            return df

        if len(scale_cols) > 0:
            df[scale_cols] = scaler.fit_transform(df[scale_cols])
        return df

    def convert_dates(self, df, date_columns):
        df = df.copy()
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception as e:
                print(f"[ERROR] Не удалось преобразовать колонку {col} в datetime: {e}")
        return df