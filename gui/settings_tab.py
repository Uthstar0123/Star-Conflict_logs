# gui/settings_tab.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.config import ConfigManager


class SettingsTab:
    def __init__(self, parent, on_config_changed):
        self.frame = ttk.Frame(parent)
        self.on_config_changed = on_config_changed

        # Заголовок
        header = ttk.Label(
            self.frame,
            text="Настройки приложения",
            font=("Arial", 12, "bold"),
            anchor="center"
        )
        header.pack(fill="x", pady=10)

        # Фрейм для настроек
        settings_frame = ttk.LabelFrame(self.frame, text="Основные настройки", padding=10)
        settings_frame.pack(fill="x", padx=20, pady=10)

        # Поле для ника
        nick_frame = ttk.Frame(settings_frame)
        nick_frame.pack(fill="x", pady=5)

        ttk.Label(nick_frame, text="Ваш ник в игре:", width=25, anchor="e").pack(side="left", padx=5)
        self.nick_entry = ttk.Entry(nick_frame, width=30)
        self.nick_entry.pack(side="left", padx=5)

        # Кнопка выбора папки с логами
        log_frame = ttk.Frame(settings_frame)
        log_frame.pack(fill="x", pady=5)

        ttk.Label(log_frame, text="Папка с логами:", width=25, anchor="e").pack(side="left", padx=5)
        self.log_path_var = tk.StringVar()
        ttk.Label(log_frame, textvariable=self.log_path_var, width=40, anchor="w",
                  relief="sunken", padding=2).pack(side="left", padx=5)

        self.browse_btn = ttk.Button(
            log_frame,
            text="📂 Выбрать папку",
            command=self.select_log_dir,
            width=15
        )
        self.browse_btn.pack(side="left", padx=5)

        # Кнопка сохранения
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.pack(fill="x", pady=15)

        self.save_btn = ttk.Button(
            btn_frame,
            text="💾 Сохранить настройки",
            command=self.save_config,
            # style="Success.TButton"

        )
        self.save_btn.pack(pady=5)

        # Загружаем текущую конфигурацию
        self.load_config()

    def load_config(self):
        """Загрузка текущей конфигурации"""
        config = ConfigManager.load()
        self.nick_entry.delete(0, tk.END)
        self.nick_entry.insert(0, config.get("nick", ""))

        log_dir = config.get("log_dir", "")
        self.log_path_var.set(log_dir if log_dir else "Не выбрана")

    def select_log_dir(self):
        """Выбор папки с логами"""
        initial_dir = self.log_path_var.get()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")

        path = filedialog.askdirectory(
            title="Выберите папку с логами Star Conflict",
            initialdir=initial_dir
        )

        if path:
            self.log_path_var.set(path)

    def save_config(self):
        """Сохранение конфигурации"""
        nick = self.nick_entry.get().strip()
        log_dir = self.log_path_var.get().strip()

        if not nick:
            messagebox.showwarning("Ошибка ника", "Пожалуйста, введите ваш ник в игре!")
            return

        if log_dir == "Не выбрана":
            messagebox.showwarning("Ошибка пути", "Пожалуйста, выберите папку с логами!")
            return

        # Сохраняем конфигурацию
        ConfigManager.save(nick, log_dir)

        # Обновляем интерфейс
        self.on_config_changed()

        messagebox.showinfo("Успех", "Настройки успешно сохранены!")