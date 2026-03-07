# gui/match_tab.py
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, messagebox

from core.data_processor import DataProcessor

from utils.config import ConfigManager


class MatchTab:
    def __init__(self, parent, main_window):  # добавили main_window
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self.ax2 = None

        # Создаём разделительную панель
        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Верхняя часть: таблица с данными
        self.tree_frame = ttk.Frame(self.paned)
        self.setup_treeview()

        # Нижняя часть: график
        self.chart_frame = ttk.Frame(self.paned)
        self.setup_chart()

        # Добавляем панели в разделитель
        self.paned.add(self.tree_frame, weight=1)
        self.paned.add(self.chart_frame, weight=1)

        self.columns = ("nick", "damage", "self_heal", "team_heal", "tank", "kills", "efficiency")
        self.last_df = None

    def update(self, df: pd.DataFrame):
        """Обновление данных в таблице и графике"""
        if df.empty:
            self.clear_all()
            return
        self.update_treeview(df)
        self.update_chart(df)

    def setup_treeview(self):
        """Создание таблицы для отображения данных"""
        # Заголовок
        header = ttk.Label(
            self.tree_frame,
            text="Данные последнего матча",
            font=("Arial", 11, "bold"),
            anchor="center"
        )
        header.pack(fill="x", pady=5)

        # Создаём Treeview
        columns = ("nick", "damage", "self_heal", "team_heal", "tank", "kills", "efficiency")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            height=10
        )

        # Настройка заголовков
        headings = {
            "nick": "Игрок",
            "damage": "Урон",
            "self_heal": "Самохил",
            "team_heal": "Исцеление союзников",
            "tank": "Танк",
            "kills": "Убийства",
            "efficiency": "Эффективность"
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100, anchor="center")

        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Упаковываем виджеты
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Сортировка по умолчанию
        self._sort_reverse = {}

        # ← сюда
        self.tree.tag_configure("even", background="#1e252e")
        self.tree.tag_configure("odd", background="#161b22")
        self.tree.tag_configure("current_player", background="#2a3b2a", font=("Arial", 10, "bold"))

    def sort_by_column(self, col):
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = {}
        self._sort_reverse[col] = not self._sort_reverse.get(col, False)

        items = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]

        if col in ["damage", "self_heal", "team_heal", "tank", "efficiency"]:
            items.sort(key=lambda x: DataProcessor.parse_number(x[0]), reverse=self._sort_reverse[col])
        elif col == "kills":
            items.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0, reverse=self._sort_reverse[col])
        else:
            items.sort(key=lambda x: str(x[0]).lower(), reverse=self._sort_reverse[col])

        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

    def setup_chart(self):
        """Создание графика с тёмной/светлой темой"""
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, 'figure'):
            plt.close(self.figure)

        self.figure = plt.figure(figsize=(10, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax2 = None

        dark_mode = self.main_window.theme['dark']
        bg_color = '#0d1117' if dark_mode else '#ffffff'
        fg_color = '#e6edf3' if dark_mode else '#000000'

        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.tick_params(colors=fg_color)
        for spine in self.ax.spines.values():
            spine.set_color(fg_color)
        self.ax.grid(True, linestyle='--', alpha=0.4, color='#30363d' if dark_mode else '#e0e0e0')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    # Правильный метод (должен быть один)
    def apply_theme(self):
        """Перерисовывает график с текущей темой и последними данными"""
        self.setup_chart()
        if self.last_df is not None:
            self.update_chart(self.last_df)

    def clear_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.ax2:
            self.ax2.remove()
            self.ax2 = None
        self.ax.clear()
        self.ax.set_title("Нет данных для отображения", fontsize=12, color="#6c757d")
        self.ax.axis('off')
        self.canvas.draw()

    def update_treeview(self, df: pd.DataFrame):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for _, row in df.iterrows():
            nick = row["nick"]
            eff = row["efficiency"] / 2 if row.get("cheat_lvl", 0) > 0 else row["efficiency"]
            mark = " ❗" if row.get("cheat_lvl", 0) > 0 else ""

            self.tree.insert("", "end", values=(
                nick + mark,
                DataProcessor.format_number(row["damage"]),
                DataProcessor.format_number(row["self_heal"]),
                DataProcessor.format_number(row["team_heal"]),
                DataProcessor.format_number(row["tank"]),
                int(row["kills"]),
                DataProcessor.format_number(eff)
            ))

        # Зебра и текущий игрок — цвета берём из main_window.theme
        even_bg = "#1e252e" if self.main_window.theme['dark'] else "#f0f0f0"
        odd_bg = "#161b22" if self.main_window.theme['dark'] else "#ffffff"
        cur_bg = "#2a3b2a" if self.main_window.theme['dark'] else "#d4edda"

        for i, item in enumerate(self.tree.get_children()):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.item(item, tags=[tag])

        # Текущий игрок
        config = ConfigManager.load()
        current_nick = config.get("nick", "")
        for item in self.tree.get_children():
            if current_nick in self.tree.item(item)["values"][0]:
                tags = list(self.tree.item(item)["tags"]) + ["current_player"]
                self.tree.item(item, tags=tags)

        # Конфигурация тегов (лучше вынести в отдельный метод, но для быстрого фикса)
        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)
        self.tree.tag_configure("current_player", background=cur_bg, font=("Arial", 10, "bold"))

    def show_cheat_banner(self, cheaters: list, max_lvl: int):
        """Показывает предупреждение о Донатерах"""
        if not cheaters:
            return
        cheaters_str = ", ".join(cheaters[:5])
        if len(cheaters) > 5:
            cheaters_str += f" и ещё {len(cheaters) - 5}"

        msg = (f"⚠️ ОБНАРУЖЕНЫ ДОНАТЕРЫ!\n\n"
               f"Игроки: {cheaters_str}\n"
               f"ЗАНЕСЛИ ГРЯЗНОМУ ГАЙДЖИНУ НА: {max_lvl} левл\n\n"
               f"Их эффективность снижена в 2 раза.")

        messagebox.showwarning("Система поиска Пидорасов АКТИВИРОВАНА", msg)

    def update_chart(self, df: pd.DataFrame):
        self.ax.clear()
        if self.ax2 is not None:
            self.ax2.remove()
            self.ax2 = None

        dark_mode = self.main_window.theme['dark']
        fg_color = '#e6edf3' if dark_mode else '#000000'
        bg_color = '#0d1117' if dark_mode else '#ffffff'

        self.ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)
        self.ax.tick_params(colors=fg_color)
        self.ax.xaxis.label.set_color(fg_color)
        self.ax.yaxis.label.set_color(fg_color)
        self.ax.title.set_color(fg_color)
        for spine in self.ax.spines.values():
            spine.set_color(fg_color)

        if df.empty:
            self.ax.set_title("Нет данных для отображения", fontsize=12, color=fg_color)
            self.canvas.draw()
            return

        players = df["nick"].tolist()
        damage = df["damage"].values
        total_heal = (df.get("self_heal", 0) + df.get("team_heal", 0)).values
        tank = df["tank"].values
        efficiency = df["efficiency"].values

        x = range(len(players))
        width = 0.25

        self.ax.bar([i - 1.5 * width for i in x], damage, width, label='Урон', color='#e74c3c')
        self.ax.bar([i - 0.5 * width for i in x], total_heal, width, label='Все исцеление', color='#2ecc71')
        self.ax.bar([i + 0.5 * width for i in x], tank, width, label='Танк', color='#3498db')

        self.ax2 = self.ax.twinx()
        self.ax2.plot(x, efficiency, 'ro-', linewidth=2, label='Эффективность')
        self.ax2.set_ylabel('Эффективность', color='#8e44ad')
        self.ax2.tick_params(axis='y', labelcolor='#8e44ad')
        self.ax2.yaxis.label.set_color('#8e44ad')

        self.ax.set_xlabel('Игроки', color=fg_color)
        self.ax.set_ylabel('Значения', color=fg_color)
        self.ax.set_title('Статистика матча', fontsize=14, fontweight='bold', color=fg_color)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(players, rotation=15, ha='right', color=fg_color)

        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        legend = self.ax.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=9)
        for text in legend.get_texts():
            text.set_color(fg_color)

        self.figure.tight_layout()
        self.canvas.draw()