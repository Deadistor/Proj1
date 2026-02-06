import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


class DataLoader:
    def load_csv(self, filepath: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(filepath)
            if df.empty:
                raise ValueError("Файл CSV пуст.")
            print(f"[INFO] CSV файл успешно загружен: {filepath}")
            return df
        except pd.errors.EmptyDataError:
            error_msg = "Файл CSV пуст или содержит только заголовки."
            print(f"[ERROR] {error_msg}")
            return None
        except pd.errors.ParserError as e:
            error_msg = f"Ошибка парсинга CSV: возможно, неверный разделитель или битый файл.\n{e}"
            print(f"[ERROR] {error_msg}")
            return None
        except PermissionError:
            error_msg = "Нет доступа к файлу (возможно, он открыт в другой программе)."
            print(f"[ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Неизвестная ошибка при загрузке CSV: {e}"
            print(f"[ERROR] {error_msg}")
            return None

    def load_excel(self, filepath: str, sheet_name=0) -> pd.DataFrame:
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            if isinstance(df, dict):
                raise ValueError("Выбрано несколько листов. Укажите один лист.")
            if df.empty:
                raise ValueError("Лист Excel пуст.")
            print(f"[INFO] Excel файл успешно загружен: {filepath}, лист: {sheet_name}")
            return df
        except ValueError as ve:
            if "No sheet named" in str(ve):
                error_msg = f"Лист '{sheet_name}' не найден в файле."
            else:
                error_msg = str(ve)
            print(f"[ERROR] {error_msg}")
            return None
        except FileNotFoundError:
            error_msg = "Файл Excel не найден."
            print(f"[ERROR] {error_msg}")
            return None
        except PermissionError:
            error_msg = "Нет доступа к файлу Excel (возможно, он открыт в другой программе)."
            print(f"[ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Ошибка при загрузке Excel: {e}"
            print(f"[ERROR] {error_msg}")
            return None

    def load_from_postgresql(self, host, port, database, user, password, sql_query) -> pd.DataFrame:
        try:
            engine = create_engine(
                f"postgresql://{user}:{password}@{host}:{port}/{database}",
                connect_args={'connect_timeout': 10}
            )
            df = pd.read_sql_query(sql_query, engine)
            if df.empty:
                print("[WARNING] Запрос выполнен, но данные пусты.")
            else:
                print("[INFO] Данные успешно загружены из PostgreSQL.")
            return df
        except SQLAlchemyError as e:
            orig = e.orig
            error_msg = f"Ошибка базы данных: {orig.pgcode}\n{orig.diag.message_detail if orig.diag else ''}"
            print(f"[ERROR] {error_msg}")
            return None
        except TimeoutError:
            error_msg = "Таймаут подключения к PostgreSQL."
            print(f"[ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Неизвестная ошибка при подключении к PostgreSQL: {e}"
            print(f"[ERROR] {error_msg}")
            return None

    def load_from_api(self, url, headers=None, params=None, expect_json=True):
        try:
            default_headers = {
                'User-Agent': 'DataLoaderApp/1.0 (https://example.com; contact@example.com)'
            }
            if headers:
                default_headers.update(headers)

            response = requests.get(url, headers=default_headers, params=params, timeout=10)
            response.raise_for_status()

            if expect_json:
                try:
                    data = response.json()
                    df = pd.json_normalize(data)
                    if df.empty:
                        print("[WARNING] JSON получен, но структура пуста.")
                    return df
                except ValueError as e:
                    error_msg = f"Ответ не в формате JSON: {e}"
                    print(f"[ERROR] {error_msg}")
                    return None
            else:
                return response.text
        except requests.exceptions.Timeout:
            error_msg = "Таймаут запроса к API."
            print(f"[ERROR] {error_msg}")
            return None
        except requests.exceptions.ConnectionError:
            error_msg = "Ошибка подключения к API (проверьте URL и интернет-соединение)."
            print(f"[ERROR] {error_msg}")
            return None
        except requests.exceptions.HTTPError as e:
            status_code = response.status_code
            error_msg = f"HTTP ошибка: {status_code} — {response.reason}"
            if 400 <= status_code < 500:
                error_msg += "\nКлиентская ошибка: проверьте токен, параметры или URL."
            elif 500 <= status_code < 600:
                error_msg += "\nСерверная ошибка: попробуйте позже."
            print(f"[ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Неизвестная ошибка при запросе к API: {e}"
            print(f"[ERROR] {error_msg}")
            return None