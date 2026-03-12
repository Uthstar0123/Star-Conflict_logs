# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from core.log_parser import LogParser   # ← здесь

import pandas as pd

from core.data_processor import DataProcessor
from utils.resource_path import resource_path
from utils.config import ConfigManager
# from utils.process_checker import is_game_running

from core.history_manager import HistoryManager
from core.log_parser import LogParser
from gui.settings_tab import SettingsTab
from gui.match_tab import MatchTab
from gui.personal_tab import PersonalTab
from gui.top_tab import TopTab
from gui.history_tab import HistoryTab


MIN_WINDOW_WIDTH = 650
MIN_WINDOW_HEIGHT = 1000

GEOMETRY = '1200x750'

class MainWindow:
    MIN_WINDOW_WIDTH = 650
    MIN_WINDOW_HEIGHT = 1000
    GEOMETRY = '1200x750'
    def __init__(
            self,
            root,
            min_window_height: int = MIN_WINDOW_HEIGHT,
            min_window_width: int = MIN_WINDOW_WIDTH,
            geometry: str = GEOMETRY
    ):
        self._min_window_height = min_window_height
        self._min_window_width = min_window_width
        self._geometry = geometry
        self.root = root
        self.root.title("Ударка_конфликт_Статик Alpha_0.16.1 By Uthstar01")
        self.root.geometry(self._geometry)
        self.root.minsize(self._min_window_height, self._min_window_width)

        self.root.iconbitmap(resource_path("icon.ico"))

        # 1. Сразу фон и прозрачность
        self.root.configure(bg='#0d1117')
        self.root.attributes('-alpha', 0.92)

        # 2. Тема
        self.theme = {
            'dark': True,
            'bg': '#0d1117',
            'fg': '#e6edf3',
            'accent': '#58a6ff',
            'hover': '#21262d',
            'selected': '#30363d',
            'alpha': 0.92
        }

        #TODO: Заменить словарь ВЫШЕ(ВЫШЕ - ЭТО СЛОВАРЬ), на dataclass(Посмотреть что это за дерьмо)
        #TODO:В каждом методе в идеале 15 строк кода, разбить конструктор на подметоды, и другие.


        self.root.configure(bg=self.theme['bg'])
        self.root.attributes('-alpha', self.theme['alpha'])

        # 3. Панель темы — САМАЯ ВЕРХНЯЯ (до всего остального)
        theme_frame = ttk.Frame(self.root)
        theme_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(theme_frame, text="Тема:").pack(side='left', padx=5)
        self.theme_var = tk.BooleanVar(value=self.theme['dark'])
        ttk.Checkbutton(theme_frame, text="Тёмная", variable=self.theme_var,
                        command=self.toggle_theme).pack(side='left', padx=5)
        ttk.Label(theme_frame, text="Прозрачность:").pack(side='left', padx=10)
        self.alpha_scale = ttk.Scale(theme_frame, from_=0.6, to=1.0, orient='horizontal',
                                     value=self.theme['alpha'], length=180,
                                     command=self._update_alpha)
        self.alpha_scale.pack(side='left', padx=5)
        self.alpha_label = ttk.Label(theme_frame, text=f"{self.theme['alpha']:.2f}")
        self.alpha_label.pack(side='left')

        # 4. Панель кнопок
        self.create_control_panel()

        # 5. Notebook и вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.settings_tab = SettingsTab(self.notebook, self.on_config_changed)
        self.match_tab   = MatchTab(self.notebook, self)
        self.personal_tab = PersonalTab(self.notebook, self)
        self.top_tab     = TopTab(self.notebook, self)

        self.history_tab = HistoryTab(self.notebook, self.on_history_match_selected)

        self.notebook.add(self.settings_tab.frame, text="⚙️ Настройки")
        self.notebook.add(self.match_tab.frame, text="🎯 Анализ матча")
        self.notebook.add(self.personal_tab.frame, text="👤 Личная статистика")
        self.notebook.add(self.top_tab.frame, text="🏆 Топ игроков")
        self.notebook.add(self.history_tab.frame, text="📜 История")
        config = ConfigManager.load()
        self.config = config
        self.theme['dark'] = config["dark_theme"]
        self.theme['alpha'] = config["alpha"]
        self.root.configure(bg=self.theme['bg'])
        self.root.attributes('-alpha', self.theme['alpha'])
        self.theme_var.set(self.theme['dark'])
        self.alpha_scale.set(self.theme['alpha'])
        self.alpha_label.config(text=f"{self.theme['alpha']:.2f}")
        self.load_initial_data()
        self.last_df = None


    def open_donate_link(self):
        import webbrowser
        donate_url = "https://www.donationalerts.com/r/restramer"  
        webbrowser.open(donate_url)

    def update(self, df: pd.DataFrame):
        self.last_df = df
        if df.empty:
            self.clear_all()
            return
        self.update_treeview(df)
        self.update_chart(df)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        bg = self.theme['bg']
        fg = self.theme['fg']
        accent = self.theme['accent']
        hover = self.theme['hover']
        selected = self.theme['selected']
        tree_fg = fg

        # Цвета для Treeview в зависимости от темы

        tree_bg = '#ffffff' if not self.theme['dark'] else '#161b22'


        style.configure('.', background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("Header.TLabel", foreground=accent, font=("Segoe UI", 14, "bold"))

        style.configure("TButton", background=hover, foreground=fg, padding=6)
        style.map("TButton", background=[('active', accent)], foreground=[('active', 'white')])

        style.configure("TNotebook", background=bg)
        style.configure("TNotebook.Tab", background=bg, foreground=fg, padding=[12, 6])
        style.map("TNotebook.Tab", background=[('selected', selected)], foreground=[('selected', fg)])

        style.configure("Treeview", background=tree_bg, fieldbackground=tree_bg)
        style.configure("Treeview.Heading", background=hover, foreground=accent)
        style.map("Treeview", background=[('selected', accent)], foreground=[('selected', 'white')])

        style.configure("TEntry", fieldbackground=bg, foreground=fg)
        style.map("TEntry", fieldbackground=[('!disabled', bg)], foreground=[('disabled', 'gray')])

    def toggle_theme(self):
        self.theme['dark'] = self.theme_var.get()
        ConfigManager.save(dark_theme=self.theme['dark'])
        if self.theme['dark']:
            self.theme.update({'bg': '#0d1117', 'fg': '#e6edf3', 'hover': '#21262d'})
        else:
            self.theme.update({'bg': '#ffffff', 'fg': '#000000', 'hover': '#f0f0f0'})
        self.root.configure(bg=self.theme['bg'])
        self.setup_styles()

        for tab in [self.match_tab, self.top_tab]:
            if hasattr(tab, 'tree'):
                tab.tree.configure(style="Treeview")

        self.match_tab.apply_theme()
        self.personal_tab.apply_theme()
        self.top_tab.apply_theme()
        self.root.update()

        even_bg = "#1e252e" if self.theme['dark'] else "#f0f0f0"
        odd_bg = "#161b22" if self.theme['dark'] else "#ffffff"
        cur_bg = "#2a3b2a" if self.theme['dark'] else "#d4edda"

        for tab in (self.match_tab, self.top_tab, self.personal_tab):
            if hasattr(tab, 'tree'):
                tab.tree.tag_configure("even", background=even_bg)
                tab.tree.tag_configure("odd", background=odd_bg)
                tab.tree.tag_configure("current_player", background=cur_bg)

        if self.match_tab.last_df is not None:
            self.match_tab.update(self.match_tab.last_df)
        if self.top_tab.last_history is not None:
            self.top_tab.update(self.top_tab.last_history)

    def _update_alpha(self, value):
        self.theme['alpha'] = float(value)
        self.root.attributes('-alpha', self.theme['alpha'])
        self.alpha_label.config(text=f"{self.theme['alpha']:.2f}")
        ConfigManager.save(alpha=self.theme['alpha'])

    def create_control_panel(self):
        panel = ttk.Frame(self.root)
        panel.pack(fill="x", padx=10, pady=10)

        ttk.Label(panel, text="Star Conflict Log Analyzer", font=("Arial", 14, "bold")).pack(side="left", padx=5)

        self.scan_btn = ttk.Button(panel, text="🔍 Матч завершен", command=self.analyze_last_match)
        self.scan_btn.pack(side="right", padx=8)

        self.donate_btn = ttk.Button(panel, text="☕ На чай", command=self.open_donate_link)
        self.donate_btn.pack(side="right", padx=5)

        self.status_var = tk.StringVar(value="Готово")
        self.status_label = ttk.Label(panel, textvariable=self.status_var)
        self.status_label.pack(side="right", padx=15)

    def analyze_last_match(self):
        if not self.config.get("log_dir"):
            messagebox.showwarning("Ошибка", "Выберите папку с логами!")
            return

        try:
            self.scan_btn.state(["disabled"])
            self.status_var.set("Сканирование последнего матча...")
            self.root.update()

            latest_match = LogParser.get_last_match_from_latest_log(self.config["log_dir"])

            if latest_match.empty:
                self.status_var.set("Последний матч не найден или пуст")
                messagebox.showinfo("Результат", "Нет данных последнего матча")
                return

            # Добавляем эффективность
            latest_match = DataProcessor.add_efficiency(latest_match)

            # Проверка читеров
            cheaters = [row["nick"] for _, row in latest_match.iterrows() if row.get("cheat_lvl", 0) > 0]
            if cheaters:
                max_lvl = latest_match["cheat_lvl"].max()
                self.match_tab.show_cheat_banner(cheaters, max_lvl)

            # Обновляем текущий матч
            self.match_tab.update(latest_match)

            # ───── АВТОМАТИЧЕСКОЕ СОХРАНЕНИЕ И ОБНОВЛЕНИЕ ВСЕХ ВКЛАДОК ─────
            LogParser.update_history(latest_match)  # сохраняем в историю
            full_history = HistoryManager.load()

            # Личная статистика
            if self.config.get("nick"):
                personal_data = full_history[full_history["nick"] == self.config["nick"]]
                self.personal_tab.update(self.config["nick"], personal_data)

            # Топ игроков
            self.top_tab.update(full_history)

            # История матчей
            self.history_tab.load_matches()

            self.status_var.set("Матч проанализирован и сохранён в историю!")

        except Exception as e:
            self.status_var.set(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось проанализировать матч:\n{str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.scan_btn.state(["!disabled"])

    def on_history_match_selected(self, match_data: pd.DataFrame):
        self.match_tab.update(match_data)  # Обновляем вкладку "Анализ матча"

    def refresh_all_data(self):
        """
        Сохраняет ПОСЛЕДНИЙ бой в историю и обновляет всю статистику.
        Используется после завершения матча, чтобы зафиксировать результат.
        """
        if not self.config.get("log_dir"):
            messagebox.showwarning("Ошибка", "Выберите папку с логами!")
            return
        if not self.config.get("nick"):
            messagebox.showwarning("Ошибка", "Укажите ваш ник!")
            return

        try:
            # self.update_btn.state(["disabled"])
            # self.status_var.set("Сохранение матча в историю...")
            # self.root.update()

            # Получаем последний бой
            latest_match = LogParser.get_last_match_from_latest_log(self.config["log_dir"])

            if latest_match.empty:
                self.status_var.set("Нет данных для сохранения")
                messagebox.showinfo("Результат", "Последний матч не найден")
                return

            # Добавляем эффективность перед сохранением
            latest_match = DataProcessor.add_efficiency(latest_match)

            # Сохраняем в историю
            LogParser.update_history(latest_match)

            # Загружаем ПОЛНУЮ историю для личной статистики
            full_history = HistoryManager.load()
            personal_data = full_history[full_history["nick"] == self.config["nick"]]

            # Обновляем вкладки
            self.personal_tab.update(self.config["nick"], personal_data)
            self.top_tab.update(full_history)  # топ по ВСЕЙ истории

            self.status_var.set("Матч сохранён в историю!")
            messagebox.showinfo("Успех", "Результаты матча добавлены в историю")

        except Exception as e:
            self.status_var.set(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить матч:\n{str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.update_btn.state(["!disabled"])

    def on_config_changed(self):
        self.config = ConfigManager.load()
        if self.config.get("nick"):
            history = HistoryManager.load()
            personal_data = history[history["nick"] == self.config["nick"]]
            self.personal_tab.update(self.config["nick"], personal_data)
            self.top_tab.update(history)  # передаём полную историю
            self.history_tab.load_matches()

    def load_initial_data(self):
        """Загружает историю сразу при открытии программы"""
        try:
            history = HistoryManager.load()
            if history.empty:
                return

            # Топ игроков
            self.top_tab.update(history)

            # Личная статистика (если ник указан)
            if self.config.get("nick"):
                personal_data = history[history["nick"] == self.config["nick"]]
                self.personal_tab.update(self.config["nick"], personal_data)

            # История матчей
            self.history_tab.load_matches()

            self.status_var.set("История загружена")
        except:

            pass  # если что-то упадёт — не мешаем запуску
