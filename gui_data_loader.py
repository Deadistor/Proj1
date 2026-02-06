import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext,filedialog
import threading
import builtins
import pandas as pd
import numpy as np
import os
# Импорты из других модулей
from data_loader import DataLoader
from data_validator import DataValidator
from data_cleaner import DataCleaner
from data_analyze import DataAnalyzer
from data_report import DataReport

class DataLoadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.loader = DataLoader()
        self.cleaner = DataCleaner()
        self.analyzer = None
        self.df = None
        self.report = None
        self.title("Загрузчик данных")
        self.geometry("900x700")

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self, text="Выберите источник данных", font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Первая строка: источники данных
        frame1 = tk.Frame(self)
        frame1.pack(pady=5)
        tk.Button(frame1, text="CSV файл", width=15, command=self.load_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="Excel файл", width=15, command=self.load_excel).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="PostgreSQL", width=15, command=self.load_postgresql).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="REST API", width=15, command=self.load_api).pack(side=tk.LEFT, padx=5)

        # Вторая строка: обработка данных
        frame2 = tk.Frame(self)
        frame2.pack(pady=5)
        tk.Button(frame2, text="Валидация данных", width=18, command=self.validate_data, bg="#FFD700").pack(
            side=tk.LEFT, padx=5)
        tk.Button(frame2, text="Очистка данных", width=15, command=self.open_cleaning_dialog, bg="#98FB98").pack(
            side=tk.LEFT, padx=5)
        tk.Button(frame2, text="Анализ данных", width=15, command=self.open_analysis_dialog, bg="#87CEEB").pack(
            side=tk.LEFT, padx=5)

        # Третья строка: отчет
        frame3 = tk.Frame(self)
        frame3.pack(pady=5)
        tk.Button(frame3, text="Отправить отчет", width=32, command=self.open_report_dialog, bg="#FFB6C1").pack()

        log_label = tk.Label(self, text="Лог и превью данных:")
        log_label.pack(anchor="w", padx=10, pady=(20, 5))

        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        v_scroll = tk.Scrollbar(text_frame, orient=tk.VERTICAL)
        h_scroll = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)

        self.log_text = tk.Text(
            text_frame,
            wrap="none",
            state="disabled",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            height=20,
            font=("Courier", 9)
        )

        v_scroll.config(command=self.log_text.yview)
        h_scroll.config(command=self.log_text.xview)

        self.log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.setup_global_shortcuts()

    def setup_global_shortcuts(self):
        self.bind_all("<Control-c>", self.global_copy)
        self.bind_all("<Control-v>", self.global_paste)
        self.bind_all("<Control-a>", self.global_select_all)

    def global_copy(self, event=None):
        widget = self.focus_get()
        if isinstance(widget, (tk.Entry, tk.Text)):
            try:
                selected = widget.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected)
            except (tk.TclError, AttributeError):
                pass
        return "break"

    def global_paste(self, event=None):
        widget = self.focus_get()
        if isinstance(widget, (tk.Entry, tk.Text)):
            try:
                text = self.clipboard_get()
                if text:
                    # Удаляем выделенный текст, если есть
                    if hasattr(widget, 'selection_get') and widget.selection_get():
                        widget.delete("sel.first", "sel.last")
                    # Вставляем новый текст
                    widget.insert(tk.INSERT, text)
            except tk.TclError:
                pass
        return "break"

    def global_select_all(self, event=None):
        widget = self.focus_get()
        if isinstance(widget, tk.Text):
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        elif isinstance(widget, tk.Entry):
            widget.select_range(0, tk.END)
        return "break"

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def show_error(self, title, message):
        messagebox.showerror(title, message)
        self.log(f"[ERROR] {title}: {message}")

    def validate_data(self):
        if self.df is None:
            self.show_error("Ошибка", "Сначала загрузите данные.")
            return

        self.log("\n[VALIDATION] Начало валидации данных...\n")

        def log_print(*args):
            self.log(" ".join(map(str, args)))

        original_print = builtins.print
        builtins.print = log_print

        try:
            DataValidator.validate_data(self.df)
        finally:
            builtins.print = original_print

    def open_cleaning_dialog(self):
        if self.df is None:
            self.show_error("Ошибка", "Сначала загрузите данные.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Очистка данных")
        dialog.geometry("400x400")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Обработка пропущенных значений:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        missing_var = tk.StringVar(value="mean")
        tk.Radiobutton(dialog, text="Заполнить средним", variable=missing_var, value="mean").pack(anchor="w", padx=40)
        tk.Radiobutton(dialog, text="Заполнить медианой", variable=missing_var, value="median").pack(anchor="w", padx=40)
        tk.Radiobutton(dialog, text="Удалить строки", variable=missing_var, value="drop").pack(anchor="w", padx=40)

        tk.Label(dialog, text="Кодирование категориальных:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        encode_var = tk.StringVar(value="onehot")
        tk.Radiobutton(dialog, text="One-Hot Encoding", variable=encode_var, value="onehot").pack(anchor="w", padx=40)
        tk.Radiobutton(dialog, text="Label Encoding", variable=encode_var, value="label").pack(anchor="w", padx=40)

        tk.Label(dialog, text="Нормализация числовых признаков:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        scale_var = tk.StringVar(value="standard")
        tk.Radiobutton(dialog, text="Стандартизация (Standard)", variable=scale_var, value="standard").pack(anchor="w", padx=40)
        tk.Radiobutton(dialog, text="Мин-макс (Min-Max)", variable=scale_var, value="minmax").pack(anchor="w", padx=40)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=30)

        def apply_cleaning():
            df_cleaned = self.df.copy()
            df_cleaned = self.cleaner.handle_missing_values(df_cleaned, strategy=missing_var.get())
            df_cleaned = self.cleaner.drop_duplicates(df_cleaned)
            df_cleaned = self.cleaner.encode_categorical(df_cleaned, method=encode_var.get())
            df_cleaned = self.cleaner.scale_numeric(df_cleaned, method=scale_var.get())
            self.df = df_cleaned
            self.clear_log()
            self.log("[INFO] Очистка данных завершена.")
            self._print_preview(df_cleaned)
            dialog.destroy()

        tk.Button(btn_frame, text="Отмена", width=10, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Применить", width=10, command=apply_cleaning, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

    def open_report_dialog(self):
        if self.df is None:
            self.show_error("Ошибка", "Сначала загрузите данные.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Генерация и отправка отчёта")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()

        # Сохраняем значения ПЕРЕД созданием потока
        entries_data = {}

        tk.Label(dialog, text="Настройки отчёта", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(dialog, text="Имя отчёта:").pack(anchor="w", padx=20)
        report_name_var = tk.StringVar(value="report")
        tk.Entry(dialog, textvariable=report_name_var, width=30).pack(pady=5)

        tk.Label(dialog, text="Директория:").pack(anchor="w", padx=20)
        out_dir_var = tk.StringVar(value="reports")
        tk.Entry(dialog, textvariable=out_dir_var, width=30).pack(pady=5)

        tk.Label(dialog, text="Форматы:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=10)
        pdf_var = tk.BooleanVar(value=True)
        excel_var = tk.BooleanVar(value=True)
        plots_var = tk.BooleanVar(value=True)
        interactive_var = tk.BooleanVar(value=True)

        tk.Checkbutton(dialog, text="PDF (ReportLab)", variable=pdf_var).pack(anchor="w", padx=40)
        tk.Checkbutton(dialog, text="Excel (openpyxl)", variable=excel_var).pack(anchor="w", padx=40)
        tk.Checkbutton(dialog, text="Графики (Matplotlib/Seaborn)", variable=plots_var).pack(anchor="w", padx=40)
        tk.Checkbutton(dialog, text="Интерактивные (Plotly)", variable=interactive_var).pack(anchor="w", padx=40)

        send_var = tk.BooleanVar()
        tk.Checkbutton(dialog, text="Отправить по email", variable=send_var).pack(anchor="w", padx=20, pady=10)

        email_frame = tk.Frame(dialog)
        email_frame.pack(fill=tk.X, padx=20, pady=5)

        grid_opts = {'sticky': 'w', 'padx': 5, 'pady': 2}
        tk.Label(email_frame, text="SMTP Хост:").grid(row=0, column=0, **grid_opts)
        smtp_host = tk.Entry(email_frame, width=20)
        smtp_host.grid(row=0, column=1, **grid_opts)
        smtp_host.insert(0, "smtp.gmail.com")

        tk.Label(email_frame, text="Порт:").grid(row=1, column=0, **grid_opts)
        smtp_port = tk.Entry(email_frame, width=20)
        smtp_port.grid(row=1, column=1, **grid_opts)
        smtp_port.insert(0, "587")

        tk.Label(email_frame, text="Email:").grid(row=2, column=0, **grid_opts)
        sender_email = tk.Entry(email_frame, width=20)
        sender_email.grid(row=2, column=1, **grid_opts)

        tk.Label(email_frame, text="Пароль:").grid(row=3, column=0, **grid_opts)
        sender_pass = tk.Entry(email_frame, width=20, show="*")
        sender_pass.grid(row=3, column=1, **grid_opts)

        tk.Label(email_frame, text="Кому:").grid(row=4, column=0, **grid_opts)
        to_emails = tk.Entry(email_frame, width=20)
        to_emails.grid(row=4, column=1, **grid_opts)
        to_emails.insert(0, "example@example.com")

        tk.Label(email_frame, text="Тема:").grid(row=5, column=0, **grid_opts)
        subject = tk.Entry(email_frame, width=20)
        subject.grid(row=5, column=1, **grid_opts)
        subject.insert(0, "Отчёт по данным")

        def generate_and_send():
            # 🔥 Считываем ВСЕ значения ДО запуска потока
            try:
                entries_data['report_name'] = report_name_var.get().strip() or "report"
                entries_data['out_dir'] = out_dir_var.get().strip() or "reports"
                entries_data['pdf'] = pdf_var.get()
                entries_data['excel'] = excel_var.get()
                entries_data['plots'] = plots_var.get()
                entries_data['interactive'] = interactive_var.get()
                entries_data['send'] = send_var.get()
                entries_data['smtp_host'] = smtp_host.get().strip()
                entries_data['smtp_port'] = smtp_port.get().strip()
                entries_data['sender_email'] = sender_email.get().strip()
                entries_data['sender_pass'] = sender_pass.get()
                entries_data['to_emails'] = to_emails.get().strip()
                entries_data['subject'] = subject.get().strip()

                # Валидация обязательных полей
                if not entries_data['sender_email']:
                    self.log("[ERROR] Email отправителя обязателен.")
                    return
                if not entries_data['sender_pass']:
                    self.log("[ERROR] Пароль обязателен.")
                    return
                if not entries_data['to_emails']:
                    self.log("[ERROR] Получатель обязателен.")
                    return

                name = entries_data['report_name']
                out_dir = entries_data['out_dir']

                self.report = DataReport(self.df, report_name=name)
                self.clear_log()
                self.log("[REPORT] Генерация отчёта...")

                def task():
                    try:
                        artifacts = self.report.build_full_report(
                            out_dir=out_dir,
                            make_pdf=entries_data['pdf'],
                            make_excel=entries_data['excel'],
                            make_static_plots=entries_data['plots'],
                            make_interactive_plots=entries_data['interactive'],
                        )
                        self.log("[REPORT] Отчёт успешно создан:")
                        for k, v in artifacts.items():
                            if isinstance(v, dict):
                                for sub_k, sub_v in v.items():
                                    self.log(f"  {k}.{sub_k}: {sub_v}")
                            else:
                                self.log(f"  {k}: {v}")

                        if entries_data['send']:
                            self.log("[REPORT] Отправка на email...")
                            try:
                                DataReport.send_full_report_smtp(
                                    artifacts=artifacts,
                                    smtp_host=entries_data['smtp_host'],
                                    smtp_port=int(entries_data['smtp_port']),
                                    username=entries_data['sender_email'],
                                    password=entries_data['sender_pass'],
                                    sender=entries_data['sender_email'],
                                    recipients=[r.strip() for r in entries_data['to_emails'].split(",")],
                                    subject=entries_data['subject'],
                                    body="Автоматически сгенерированный отчёт прикреплён.",
                                    use_tls=True,
                                )
                                self.log("[REPORT] ✅ Отчёт успешно отправлен по email.")
                            except Exception as e:
                                self.log(f"[ERROR] Отправка не удалась: {type(e).__name__}: {e}")
                        else:
                            self.log(f"[REPORT] 📁 Путь к файлам: {os.path.abspath(out_dir)}")

                    except Exception as e:
                        self.log(f"[ERROR] Ошибка при генерации/отправке: {e}")

                threading.Thread(target=task, daemon=True).start()
                dialog.destroy()

            except Exception as e:
                self.log(f"[ERROR] Ошибка в диалоге отчёта: {e}")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Отмена", width=10, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Создать", width=10, command=generate_and_send, bg="#4CAF50", fg="white").pack(
            side=tk.LEFT, padx=5)

    def open_analysis_dialog(self):
        if self.df is None:
            self.show_error("Ошибка", "Сначала загрузите данные.")
            return

        self.analyzer = DataAnalyzer(self.df)
        self.analyzer.set_log_func(self.log)
        dialog = tk.Toplevel(self)
        dialog.title("Анализ данных")
        dialog.geometry("500x250")
        dialog.transient(self)
        dialog.grab_set()

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Статистика
        stats_tab = tk.Frame(notebook)
        notebook.add(stats_tab, text="Статистика")
        tk.Button(stats_tab, text="Показать статистики", command=self.run_basic_stats).pack(pady=20)

        # Аномалии
        anomaly_tab = tk.Frame(notebook)
        notebook.add(anomaly_tab, text="Аномалии")
        tk.Label(anomaly_tab, text="Порог Z-score:").pack(pady=5)
        z_var = tk.DoubleVar(value=3.0)
        tk.Entry(anomaly_tab, textvariable=z_var, width=10).pack(pady=5)
        tk.Button(anomaly_tab, text="Найти выбросы", command=lambda: self.run_find_anomalies(z_var.get())).pack(pady=10)

        # Регрессия
        reg_tab = tk.Frame(notebook)
        notebook.add(reg_tab, text="Регрессия")

        tk.Label(reg_tab, text="Целевая переменная:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=5)
        target_reg = tk.StringVar()
        cols_num = [col for col in self.df.select_dtypes(include=[np.number]).columns]
        ttk.Combobox(reg_tab, textvariable=target_reg, values=cols_num).pack(fill=tk.X, padx=20, pady=5)

        # Добавьте выбор модели (и объявите model_reg_var)
        tk.Label(reg_tab, text="Модель:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=5)
        model_reg_var = tk.StringVar(value="linear")  # 🔽 Объявлена здесь
        tk.Radiobutton(reg_tab, text="Линейная регрессия", variable=model_reg_var, value="linear").pack(anchor="w",
                                                                                                        padx=40)
        tk.Radiobutton(reg_tab, text="Случайный лес", variable=model_reg_var, value="random_forest").pack(anchor="w",
                                                                                                          padx=40)

        # Кнопка обучения
        tk.Button(reg_tab, text="Обучить регрессию",
                  command=lambda: self.run_regression(target_reg.get(), model_reg_var.get())).pack(pady=10)

       # Классификация
        clf_tab = tk.Frame(notebook)
        notebook.add(clf_tab, text="Классификация")
        tk.Label(clf_tab, text="Целевая переменная:").pack(pady=5)
        target_clf = tk.StringVar()
        cols_cat = [c for c in self.df.columns if self.df[c].dtype == 'object' or self.df[c].nunique() <= 20]
        ttk.Combobox(clf_tab, textvariable=target_clf, values=cols_cat).pack(pady=5)

        tk.Label(clf_tab, text="Модель:").pack(pady=5)
        model_var = tk.StringVar(value="logistic")
        tk.Radiobutton(clf_tab, text="Logistic Regression", variable=model_var, value="logistic").pack()
        tk.Radiobutton(clf_tab, text="Random Forest", variable=model_var, value="random_forest").pack()

        tk.Button(clf_tab, text="Обучить классификацию",
                  command=lambda: self.run_classification(target_clf.get(), model_var.get())).pack(pady=10)

    def run_basic_stats(self):
        self.clear_log()
        self.log("[ANALYSIS] Расчет базовых статистик...")

        def task():
            self.analyzer.basic_statistics()

        threading.Thread(target=task, daemon=True).start()

    def run_find_anomalies(self, z_thresh):
        self.clear_log()
        self.log(f"[ANALYSIS] Поиск аномалий с Z > {z_thresh}...")

        def task():
            self.analyzer.find_anomalies(z_thresh)

        threading.Thread(target=task, daemon=True).start()

    def run_regression(self, target, model_type):
        if not target:
            self.show_error("Ошибка", "Выберите целевую переменную.")
            return
        self.clear_log()
        self.log(f"[ANALYSIS] Обучение модели: {model_type}, цель: {target}")

        def task():
            self.analyzer.build_regression_model(target_column=target, model_type=model_type)

        threading.Thread(target=task, daemon=True).start()

    def run_classification(self, target, model_type):
        if not target:
            self.show_error("Ошибка", "Выберите целевую переменную.")
            return
        self.clear_log()
        self.log(f"[ANALYSIS] Обучение модели: {model_type}, цель: {target}")

        def task():
            self.analyzer.build_classification_model(target, model_type)

        threading.Thread(target=task, daemon=True).start()

    def _print_preview(self, df, n=5):
        self.log(f"Размер данных: {df.shape[0]} строк × {df.shape[1]} столбцов")

        if df.empty:
            self.log("\n[INFO] Данные пусты.")
            return

        sample = df.head(n)
        col_widths = {}
        for col in df.columns:
            max_len = max(
                len(str(col)),
                df[col].head(n).apply(lambda x: len(str(x)) if pd.notna(x) else 3).max()
            )
            col_widths[col] = min(max_len, 30)

        header = "  ".join(f"{str(col):<{col_widths[col]}}" for col in df.columns)
        self.log("\n" + header)
        self.log("-" * len(header))

        for i, row in sample.iterrows():
            values = [
                f"{str(row[col]) if pd.notna(row[col]) else 'NaN':<{col_widths[col]}}"
                for col in df.columns
            ]
            self.log("  ".join(values))

        if len(df) > n:
            self.log(f"... и ещё {len(df) - n} строк.")

    def load_csv(self):
        path = tk.filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        self.clear_log()
        self.log(f"[INFO] Выбран CSV: {path}")

        def task():
            df = self.loader.load_csv(path)
            if df is not None:
                self.df = df
                self._print_preview(df)
            else:
                self.show_error("Ошибка загрузки CSV", "Не удалось загрузить файл. Проверьте путь и формат.")

        threading.Thread(target=task, daemon=True).start()

    def load_excel(self):
        path = tk.filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not path:
            return

        sheet = self.simple_input("Sheet name", "Введите имя листа или номер (по умолчанию 0):", "0")
        if sheet == "":
            sheet = 0
        try:
            sheet = int(sheet)
        except ValueError:
            pass

        self.clear_log()
        self.log(f"[INFO] Выбран Excel: {path}, лист: {sheet}")

        def task():
            df = self.loader.load_excel(path, sheet_name=sheet)
            if df is not None:
                self.df = df
                self._print_preview(df)
            else:
                self.show_error("Ошибка загрузки Excel", "Проверьте путь, формат файла и имя листа.")

        threading.Thread(target=task, daemon=True).start()

    def load_postgresql(self):
        dialog = tk.Toplevel(self)
        dialog.title("Подключение к PostgreSQL")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        fields = {}
        row = 0
        for label_text, key, default in [
            ("Host:", "host", "localhost"),
            ("Port:", "port", "5432"),
            ("Database:", "database", ""),
            ("User:", "user", ""),
            ("Password:", "password", "")
        ]:
            tk.Label(dialog, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(dialog, width=40, show="*" if key == "password" else "")
            entry.insert(0, default)
            entry.grid(row=row, column=1, padx=10, pady=5)
            fields[key] = entry
            row += 1

        tk.Label(dialog, text="SQL Запрос:").grid(row=row, column=0, sticky="nw", padx=10, pady=5)
        sql_text = scrolledtext.ScrolledText(dialog, height=8, width=40)
        sql_text.grid(row=row, column=1, padx=10, pady=5)

        def on_ok():
            values = {k: e.get().strip() for k, e in fields.items()}
            sql_query = sql_text.get("1.0", tk.END).strip()
            if not sql_query:
                messagebox.showerror("Ошибка", "SQL-запрос не может быть пустым.")
                return
            dialog.destroy()

            self.clear_log()
            self.log("[INFO] Подключение к PostgreSQL...")

            def task():
                df = self.loader.load_from_postgresql(
                    host=values["host"],
                    port=int(values["port"]),
                    database=values["database"],
                    user=values["user"],
                    password=values["password"],
                    sql_query=sql_query
                )
                if df is not None:
                    self.df = df
                    self._print_preview(df)
                else:
                    self.show_error("Ошибка PostgreSQL", "Проверьте параметры подключения и SQL-запрос.")

            threading.Thread(target=task, daemon=True).start()

        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=row + 1, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Отмена", width=10, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Загрузить", width=10, command=on_ok).pack(side=tk.LEFT, padx=5)

    def load_api(self):
        dialog = tk.Toplevel(self)
        dialog.title("Загрузка из API")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="URL:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        url_entry = tk.Entry(dialog, width=40)
        url_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Тип ответа:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        json_var = tk.BooleanVar(value=True)
        tk.Radiobutton(dialog, text="JSON", variable=json_var, value=True).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(dialog, text="Текст/HTML", variable=json_var, value=False).grid(row=2, column=1, sticky="w")

        tk.Label(dialog, text="Authorization Token (опционально):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        token_entry = tk.Entry(dialog, width=40)
        token_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Префикс (Bearer, Token и т.п.):").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        prefix_entry = tk.Entry(dialog, width=40)
        prefix_entry.insert(0, "Bearer")
        prefix_entry.grid(row=4, column=1, padx=10, pady=5)

        def on_ok():
            url = url_entry.get().strip()
            expect_json = json_var.get()
            token = token_entry.get().strip()
            prefix = prefix_entry.get().strip()

            if not url:
                messagebox.showerror("Ошибка", "URL обязателен.")
                return

            headers = {}
            if token:
                headers["Authorization"] = f"{prefix} {token}".strip()

            dialog.destroy()
            self.clear_log()
            self.log(f"[INFO] Загрузка из API: {url}")

            def task():
                df = self.loader.load_from_api(url, headers=headers, expect_json=expect_json)
                if isinstance(df, pd.DataFrame):
                    self.df = df
                    self._print_preview(df)
                elif isinstance(df, str):
                    self.log("\n[INFO] Получен текстовый ответ:")
                    self.log(df[:2000])
                else:
                    self.show_error("Ошибка API", "Не удалось получить данные. Проверьте URL, токен и формат ответа.")

            threading.Thread(target=task, daemon=True).start()

        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        tk.Button(btn_frame, text="Отмена", width=10, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Загрузить", width=10, command=on_ok).pack(side=tk.LEFT, padx=5)

    def simple_input(self, title, prompt, default=""):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=prompt).pack(pady=10)
        entry = tk.Entry(dialog, width=50)
        entry.pack(pady=5)
        entry.insert(0, default)
        entry.focus_set()

        result = {"value": None}

        def on_ok():
            result["value"] = entry.get()
            dialog.destroy()  # 🔴 Было: dialog.destroy

        def on_cancel():
            result["value"] = ""
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Отмена", width=10, command=on_cancel).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="ОК", width=10, command=on_ok).pack(side=tk.LEFT, padx=5)

        self.wait_window(dialog)
        return result["value"]