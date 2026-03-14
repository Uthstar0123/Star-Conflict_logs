import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import pandas as pd

from core.data_processor import DataProcessor
from core.history_manager import HistoryManager
from core.log_parser import LogParser
from gui.history_tab import HistoryTab
from gui.match_tab import MatchTab
from gui.personal_tab import PersonalTab
from gui.settings_tab import SettingsTab
from gui.top_tab import TopTab
from utils.config import ConfigManager
from utils.resource_path import resource_path

MIN_WINDOW_WIDTH = 980
MIN_WINDOW_HEIGHT = 680
GEOMETRY = "1220x780"


class MainWindow:
    def __init__(
        self,
        root,
        min_window_height: int = MIN_WINDOW_HEIGHT,
        min_window_width: int = MIN_WINDOW_WIDTH,
        geometry: str = GEOMETRY,
    ):
        self.root = root
        self._min_window_height = min_window_height
        self._min_window_width = min_window_width
        self._geometry = geometry

        self.config = ConfigManager.load()
        self.theme = {
            "dark": bool(self.config.get("dark_theme", True)),
            "alpha": float(self.config.get("alpha", 0.96)),
        }
        self._apply_theme_palette()

        self._configure_root_window()
        self.setup_styles()

        self.create_header_panel()
        self.create_control_panel()
        self.create_tabs()

        self.last_df = None
        self.load_initial_data()

    def _apply_theme_palette(self):
        if self.theme["dark"]:
            self.theme.update(
                {
                    "bg": "#0f1720",
                    "panel": "#182433",
                    "card": "#111b27",
                    "fg": "#e6eef8",
                    "muted": "#9ab0c9",
                    "accent": "#1f8ef1",
                    "accent_alt": "#2bbf7f",
                    "warning": "#f4b740",
                }
            )
        else:
            self.theme.update(
                {
                    "bg": "#f4f7fb",
                    "panel": "#e8eef5",
                    "card": "#ffffff",
                    "fg": "#1b2430",
                    "muted": "#607086",
                    "accent": "#0f6ad6",
                    "accent_alt": "#148a7b",
                    "warning": "#c47c00",
                }
            )

    def _configure_root_window(self):
        self.root.title("Star Conflict Combat Analyzer")
        self.root.geometry(self._geometry)
        self.root.minsize(self._min_window_width, self._min_window_height)

        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass

        self.root.configure(bg=self.theme["bg"])
        try:
            self.root.attributes("-alpha", self.theme["alpha"])
        except tk.TclError:
            pass

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = self.theme["bg"]
        panel = self.theme["panel"]
        card = self.theme["card"]
        fg = self.theme["fg"]
        muted = self.theme["muted"]
        accent = self.theme["accent"]

        style.configure(".", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)

        style.configure("Header.TLabel", font=("Bahnschrift SemiBold", 16), foreground=accent)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground=muted)
        style.configure("Section.TLabel", font=("Bahnschrift SemiBold", 11), foreground=accent)
        style.configure("StatValue.TLabel", font=("Bahnschrift SemiBold", 10), foreground=fg)
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground=muted)

        style.configure("TButton", background=panel, foreground=fg, padding=(10, 8), borderwidth=0)
        style.map("TButton", background=[("active", card), ("pressed", panel)])

        style.configure(
            "Accent.TButton",
            background=accent,
            foreground="white",
            font=("Bahnschrift SemiBold", 10),
            padding=(14, 8),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#3da0fb"), ("pressed", "#0c5fbf")],
            foreground=[("active", "white"), ("pressed", "white")],
        )

        style.configure("Ghost.TButton", background=panel, foreground=fg, padding=(12, 8), borderwidth=0)
        style.map("Ghost.TButton", background=[("active", card), ("pressed", panel)])

        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=panel,
            foreground=muted,
            padding=(14, 9),
            font=("Bahnschrift SemiBold", 10),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", card), ("active", panel)],
            foreground=[("selected", fg), ("active", fg)],
        )

        style.configure(
            "Treeview",
            background=card,
            fieldbackground=card,
            foreground=fg,
            rowheight=27,
            bordercolor=panel,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=panel,
            foreground=accent,
            relief="flat",
            font=("Bahnschrift SemiBold", 10),
        )
        style.map(
            "Treeview",
            background=[("selected", accent)],
            foreground=[("selected", "white")],
        )

        style.configure("TLabelframe", background=bg, borderwidth=1, relief="solid")
        style.configure(
            "TLabelframe.Label",
            background=bg,
            foreground=muted,
            font=("Bahnschrift SemiBold", 9),
        )

        style.configure("TCheckbutton", background=bg, foreground=fg)
        style.configure("TEntry", fieldbackground=card, foreground=fg)
        style.configure("Horizontal.TScale", background=bg, troughcolor=panel)

    def create_header_panel(self):
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=12, pady=(12, 4))

        left = ttk.Frame(header)
        left.pack(side="left", fill="x", expand=True)

        ttk.Label(left, text="Star Conflict Combat Analyzer", style="Header.TLabel").pack(
            side="top", anchor="w"
        )
        ttk.Label(
            left,
            text="Сканирование последнего матча, история и персональный прогресс",
            style="SubHeader.TLabel",
        ).pack(side="top", anchor="w", pady=(2, 0))

        right = ttk.Frame(header)
        right.pack(side="right", anchor="e")

        self.theme_var = tk.BooleanVar(value=self.theme["dark"])
        ttk.Label(right, text="Тёмная тема").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Checkbutton(right, variable=self.theme_var, command=self.toggle_theme).grid(
            row=0, column=1, sticky="w"
        )

        ttk.Label(right, text="Прозрачность").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(6, 0))
        self.alpha_scale = ttk.Scale(
            right,
            from_=0.65,
            to=1.0,
            orient="horizontal",
            value=self.theme["alpha"],
            length=160,
            command=self._update_alpha,
        )
        self.alpha_scale.grid(row=1, column=1, sticky="ew", pady=(6, 0))

        self.alpha_label = ttk.Label(right, text=f"{self.theme['alpha']:.2f}", style="SubHeader.TLabel")
        self.alpha_label.grid(row=1, column=2, sticky="w", padx=(8, 0), pady=(6, 0))

    def create_control_panel(self):
        panel = ttk.Frame(self.root)
        panel.pack(fill="x", padx=12, pady=(4, 10))

        self.scan_btn = ttk.Button(
            panel,
            text="Анализ последнего матча",
            command=self.analyze_last_match,
            style="Accent.TButton",
        )
        self.scan_btn.pack(side="left", padx=(0, 8))

        self.donate_btn = ttk.Button(
            panel,
            text="Поддержать проект",
            command=self.open_donate_link,
            style="Ghost.TButton",
        )
        self.donate_btn.pack(side="left")

        status_frame = ttk.Frame(panel)
        status_frame.pack(side="right")
        ttk.Label(status_frame, text="Статус:", style="SubHeader.TLabel").pack(side="left", padx=(0, 6))

        self.status_var = tk.StringVar(value="Готово к анализу")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side="left")

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.settings_tab = SettingsTab(self.notebook, self.on_config_changed)
        self.match_tab = MatchTab(self.notebook, self)
        self.personal_tab = PersonalTab(self.notebook, self)
        self.top_tab = TopTab(self.notebook, self)
        self.history_tab = HistoryTab(self.notebook, self.on_history_match_selected)

        self.notebook.add(self.settings_tab.frame, text="Настройки")
        self.notebook.add(self.match_tab.frame, text="Анализ матча")
        self.notebook.add(self.personal_tab.frame, text="Личная статистика")
        self.notebook.add(self.top_tab.frame, text="Топ игроков")
        self.notebook.add(self.history_tab.frame, text="История")

    def open_donate_link(self):
        webbrowser.open("https://www.donationalerts.com/r/restramer")

    def update(self, df: pd.DataFrame):
        self.last_df = df
        if df is None:
            self.match_tab.update(pd.DataFrame())
            return
        self.match_tab.update(df)

    def toggle_theme(self):
        self.theme["dark"] = bool(self.theme_var.get())
        ConfigManager.save(dark_theme=self.theme["dark"])

        self._apply_theme_palette()
        self.root.configure(bg=self.theme["bg"])
        self.setup_styles()

        self.match_tab.apply_theme()
        self.personal_tab.apply_theme()
        self.top_tab.apply_theme()
        self.history_tab.load_matches()

        self.root.update_idletasks()

    def _update_alpha(self, value):
        try:
            alpha = float(value)
        except (TypeError, ValueError):
            return

        self.theme["alpha"] = max(0.65, min(alpha, 1.0))
        self.alpha_label.config(text=f"{self.theme['alpha']:.2f}")

        try:
            self.root.attributes("-alpha", self.theme["alpha"])
        except tk.TclError:
            pass

        ConfigManager.save(alpha=self.theme["alpha"])

    def analyze_last_match(self):
        self.config = ConfigManager.load()

        if not self.config.get("log_dir"):
            messagebox.showwarning("Ошибка", "Выберите папку с логами в настройках.")
            return

        try:
            self.scan_btn.state(["disabled"])
            self.status_var.set("Сканирование последнего матча...")
            self.root.update_idletasks()

            latest_match = LogParser.get_last_match_from_latest_log(self.config["log_dir"])
            if latest_match.empty:
                self.status_var.set("Последний матч не найден")
                messagebox.showinfo("Результат", "Нет данных последнего матча.")
                return

            latest_match = DataProcessor.add_efficiency(latest_match)

            cheaters = [
                row["nick"]
                for _, row in latest_match.iterrows()
                if int(row.get("cheat_lvl", 0) or 0) > 0
            ]
            if cheaters:
                if "cheat_lvl" in latest_match.columns:
                    max_lvl = int(pd.to_numeric(latest_match["cheat_lvl"], errors="coerce").fillna(0).max())
                else:
                    max_lvl = 0
                self.match_tab.show_cheat_banner(cheaters, max_lvl)

            self.match_tab.update(latest_match)

            LogParser.update_history(latest_match)
            full_history = HistoryManager.load()

            nick = self.config.get("nick", "").strip()
            if nick:
                personal_data = full_history[full_history["nick"] == nick]
                self.personal_tab.update(nick, personal_data)
            else:
                self.personal_tab.clear_all()

            self.top_tab.update(full_history)
            self.history_tab.load_matches()

            self.status_var.set(f"Матч обработан: {len(latest_match)} игроков")

        except Exception as e:
            self.status_var.set(f"Ошибка: {e}")
            messagebox.showerror("Ошибка", f"Не удалось проанализировать матч:\n{e}")
        finally:
            self.scan_btn.state(["!disabled"])

    def on_history_match_selected(self, match_data: pd.DataFrame):
        if match_data is None or match_data.empty:
            self.match_tab.update(pd.DataFrame())
            return

        safe_match = match_data.copy()
        if "nick" in safe_match.columns:
            safe_match["nick"] = safe_match["nick"].fillna("").astype(str).str.strip()
            safe_match = safe_match[safe_match["nick"] != ""]
            safe_match = safe_match.drop_duplicates(subset=["nick"], keep="last")

        if "efficiency" not in safe_match.columns:
            safe_match = DataProcessor.add_efficiency(safe_match)

        self.match_tab.update(safe_match)

        if "match_date" in safe_match.columns and not safe_match.empty:
            self.status_var.set(f"Открыт матч из истории: {safe_match['match_date'].iloc[0]}")

    def refresh_all_data(self):
        self.analyze_last_match()

    def on_config_changed(self):
        self.config = ConfigManager.load()
        history = HistoryManager.load()

        nick = self.config.get("nick", "").strip()
        if nick:
            personal_data = history[history["nick"] == nick]
            self.personal_tab.update(nick, personal_data)
        else:
            self.personal_tab.clear_all()

        self.top_tab.update(history)
        self.history_tab.load_matches()

    def load_initial_data(self):
        try:
            history = HistoryManager.load()
            if history.empty:
                self.status_var.set("История пуста")
                return

            self.top_tab.update(history)

            nick = self.config.get("nick", "").strip()
            if nick:
                personal_data = history[history["nick"] == nick]
                self.personal_tab.update(nick, personal_data)

            self.history_tab.load_matches()
            self.status_var.set("История загружена")
        except Exception:
            self.status_var.set("Ошибка загрузки истории")
