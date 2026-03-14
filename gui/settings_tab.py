import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from utils.config import ConfigManager


class SettingsTab:
    def __init__(self, parent, on_config_changed):
        self.frame = ttk.Frame(parent)
        self.on_config_changed = on_config_changed

        header = ttk.Label(
            self.frame,
            text="Настройки приложения",
            style="Section.TLabel",
            anchor="center",
        )
        header.pack(fill="x", pady=10)

        settings_frame = ttk.LabelFrame(self.frame, text="Параметры", padding=12)
        settings_frame.pack(fill="x", padx=18, pady=10)

        nick_row = ttk.Frame(settings_frame)
        nick_row.pack(fill="x", pady=6)
        ttk.Label(nick_row, text="Ваш ник в игре:", width=24, anchor="e").pack(side="left", padx=6)
        self.nick_entry = ttk.Entry(nick_row, width=36)
        self.nick_entry.pack(side="left", padx=6)

        log_row = ttk.Frame(settings_frame)
        log_row.pack(fill="x", pady=6)

        ttk.Label(log_row, text="Папка с логами:", width=24, anchor="e").pack(side="left", padx=6)
        self.log_path_var = tk.StringVar(value="Не выбрана")

        path_label = ttk.Label(
            log_row,
            textvariable=self.log_path_var,
            width=58,
            anchor="w",
            relief="sunken",
            padding=4,
        )
        path_label.pack(side="left", padx=6, fill="x", expand=True)

        self.browse_btn = ttk.Button(
            log_row,
            text="Выбрать",
            command=self.select_log_dir,
            style="Ghost.TButton",
            width=12,
        )
        self.browse_btn.pack(side="left", padx=6)

        btn_row = ttk.Frame(settings_frame)
        btn_row.pack(fill="x", pady=14)

        self.save_btn = ttk.Button(
            btn_row,
            text="Сохранить настройки",
            command=self.save_config,
            style="Accent.TButton",
        )
        self.save_btn.pack()

        self.load_config()

    def load_config(self):
        config = ConfigManager.load()
        self.nick_entry.delete(0, tk.END)
        self.nick_entry.insert(0, config.get("nick", ""))

        log_dir = config.get("log_dir", "")
        self.log_path_var.set(log_dir if log_dir else "Не выбрана")

    def select_log_dir(self):
        current_dir = self.log_path_var.get().strip()
        if not current_dir or current_dir == "Не выбрана" or not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")

        path = filedialog.askdirectory(
            title="Выберите папку с логами Star Conflict",
            initialdir=current_dir,
        )

        if path:
            self.log_path_var.set(path)

    def save_config(self):
        nick = self.nick_entry.get().strip()
        log_dir = self.log_path_var.get().strip()

        if not nick:
            messagebox.showwarning("Ошибка", "Введите ваш ник в игре.")
            return

        if not log_dir or log_dir == "Не выбрана":
            messagebox.showwarning("Ошибка", "Выберите папку с логами.")
            return

        if not os.path.isdir(log_dir):
            messagebox.showwarning("Ошибка", "Указанная папка логов не существует.")
            return

        ConfigManager.save(nick=nick, log_dir=log_dir)
        self.on_config_changed()
        messagebox.showinfo("Готово", "Настройки сохранены.")
