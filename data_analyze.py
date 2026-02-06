import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from statsmodels.tsa.seasonal import seasonal_decompose


class DataAnalyzer:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.log_func = None  # Будет установлена извне

    def set_log_func(self, log_func):
        """Установка функции логирования для вывода в GUI"""
        self.log_func = log_func

    def _log_print(self, *args):
        """Вывод в GUI-лог вместо терминала"""
        if self.log_func:
            self.log_func(" ".join(map(str, args)))
        else:
            print(" ".join(map(str, args)))

    def basic_statistics(self):
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            self._log_print("[ANALYSIS] Нет числовых колонок для статистики.")
            return

        stats = {
            "mean": numeric_df.mean(),
            "median": numeric_df.median(),
            "mode": numeric_df.mode().iloc[0] if not numeric_df.mode().empty else np.nan,
            "std": numeric_df.std(),
            "min": numeric_df.min(),
            "max": numeric_df.max()
        }
        stats_df = pd.DataFrame(stats)
        self._log_print("\n[ANALYSIS] Базовые статистики:")
        self._log_print(stats_df.to_string())

    def find_anomalies(self, z_thresh=3.0):
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            self._log_print("[ANALYSIS] Нет числовых колонок для поиска выбросов.")
            return

        z_scores = np.abs((numeric_df - numeric_df.mean()) / (numeric_df.std() + 1e-8))
        anomalies = self.df[(z_scores > z_thresh).any(axis=1)]
        self._log_print(f"\n[ANALYSIS] Найдено выбросов (Z > {z_thresh}): {len(anomalies)}")
        if len(anomalies) > 0:
            self._log_print("Примеры аномалий:")
            self._log_print(str(anomalies.head()))
        else:
            self._log_print("Аномалий не найдено.")

    def build_regression_model(self, target_column: str, model_type="linear"):
        if target_column not in self.df.columns:
            self._log_print(f"[ERROR] Целевая колонка '{target_column}' не найдена.")
            return

        X = self.df.drop(columns=[target_column]).select_dtypes(include=[np.number]).dropna()
        y = self.df[target_column].loc[X.index]

        if X.empty or y.empty:
            self._log_print("[ERROR] Нет данных после очистки.")
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if model_type == "linear":
            model = LinearRegression()
        elif model_type == "random_forest":
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(random_state=42)
        else:
            self._log_print(f"[ERROR] Неизвестная модель: {model_type}")
            return

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        self._log_print("\n[ANALYSIS] Метрики регрессии:")
        self._log_print(f"RMSE: {rmse:.4f}")
        self._log_print(f"MAE: {mae:.4f}")
        self._log_print(f"R²: {r2:.4f}")

    def build_classification_model(self, target_column: str, model_type="logistic"):
        if target_column not in self.df.columns:
            self._log_print(f"[ERROR] Целевая колонка '{target_column}' не найдена.")
            return

        X = self.df.drop(columns=[target_column]).select_dtypes(include=[np.number]).dropna()
        y = self.df[target_column].loc[X.index]

        if X.empty or y.empty:
            self._log_print("[ERROR] Нет данных после очистки.")
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        if model_type == "logistic":
            model = LogisticRegression(max_iter=200, random_state=42)
        elif model_type == "random_forest":
            model = RandomForestClassifier(random_state=42)
        else:
            self._log_print(f"[ERROR] Неизвестная модель: {model_type}")
            return

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1], multi_class='ovr') \
            if hasattr(model, 'predict_proba') and len(np.unique(y)) == 2 else np.nan

        self._log_print("\n[ANALYSIS] Метрики классификации:")
        self._log_print(f"Accuracy: {accuracy:.4f}")
        self._log_print(f"Precision: {precision:.4f}")
        self._log_print(f"Recall: {recall:.4f}")
        self._log_print(f"F1: {f1:.4f}")
        self._log_print(f"ROC-AUC: {auc:.4f}" if not np.isnan(auc) else "ROC-AUC: недоступен")