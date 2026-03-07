# gui/top_tab.py
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.data_processor import DataProcessor
from core.history_manager import HistoryManager
from tkinter import ttk
import pandas as pd
import numpy as np
from utils.config import ConfigManager

import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="Tight layout not applied.")


class TopTab:
    def __init__(self, parent, main_window):  # добавили main_window
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        # Создаём разделительную панель
        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Верхняя часть: таблица с топом
        self.table_frame = ttk.Frame(self.paned)
        self.setup_table()

        # Нижняя часть: круговые диаграммы
        self.chart_frame = ttk.Frame(self.paned)
        self.setup_chart()

        self.tree_data = []

        # Добавляем панели в разделитель
        self.paned.add(self.table_frame, weight=1)
        self.paned.add(self.chart_frame, weight=1)

        self.last_history = None

    def update(self, match_data: pd.DataFrame = None):
        self.last_history = match_data  # <-- добавить
        if match_data is None or match_data.empty:
            self.clear_all()
            return
        self.update_table(match_data)
        self.update_charts(match_data)

    def apply_theme(self):
        """Перерисовывает графики с текущей темой и последними данными"""
        self.setup_chart()
        if self.last_history is not None:
            self.update_charts(self.last_history)
            self.update_table(self.last_history)

    def setup_table(self):
        header = ttk.Label(
            self.table_frame,
            text="Топ игроков по эффективности",
            font=("Arial", 11, "bold"),
            anchor="center"
        )
        header.pack(fill="x", pady=5)

        columns = ("rank", "nick", "matches", "avg_damage", "avg_heal", "avg_tank", "avg_efficiency")
        self.tree = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            height=25
        )

        headings = {
            "rank": "Место",
            "nick": "Игрок",
            "matches": "Матчей",
            "avg_damage": "Средний урон",
            "avg_heal": "Средний хил",
            "avg_tank": "Средний танк",
            "avg_efficiency": "Средняя эффективность"
        }

        widths = {
            "rank": 50, "nick": 120, "matches": 80, "avg_damage": 100,
            "avg_heal": 100, "avg_tank": 100, "avg_efficiency": 150
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    # def sort_by_column(self, col):
    #     # Простая сортировка по клику (без сохранения состояния)
    #     items = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
    #
    #     if col in ["avg_damage", "avg_heal", "avg_tank", "avg_efficiency"]:
    #         try:
    #             items.sort(key=lambda x: float(x[0]) if x[0] else 0, reverse=True)
    #         except ValueError:
    #             items.sort(key=lambda x: x[0], reverse=True)
    #     elif col == "matches":
    #         items.sort(key=lambda x: int(x[0]) if x[0] else 0, reverse=True)
    #     else:
    #         items.sort(key=lambda x: x[0].lower(), reverse=True)
    #
    #     for index, (_, item) in enumerate(items):
    #         self.tree.move(item, '', index)

    def sort_by_column(self, col):
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = {}
        self._sort_reverse[col] = not self._sort_reverse.get(col, False)
        reverse = self._sort_reverse[col]

        # Получаем все строки
        items = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]

        if col == "rank":
            # Числовая сортировка по месту (1, 2, 3..., а не 1, 10, 11...)
            items.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 999, reverse=reverse)

        elif col in ["avg_damage", "avg_heal", "avg_tank", "avg_efficiency"]:
            # Сортировка по настоящему числу (а не по строке "1.2к")
            items.sort(key=lambda x: DataProcessor.parse_number(x[0]), reverse=reverse)

        elif col == "matches":
            items.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0, reverse=reverse)

        else:  # ник
            items.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)

        # Применяем новую сортировку
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

        # Принудительно обновляем таблицу
        self.tree.update_idletasks()

    def setup_chart(self):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, 'figure'):
            plt.close(self.figure)

        self.figure, self.axes = plt.subplots(1, 3, figsize=(12, 4))

        dark_mode = self.main_window.theme['dark']
        bg_color = '#0d1117' if dark_mode else '#ffffff'
        fg_color = '#e6edf3' if dark_mode else '#000000'

        self.figure.patch.set_facecolor(bg_color)

        for ax in self.axes:
            ax.set_facecolor(bg_color)
            ax.tick_params(colors=fg_color)
            for spine in ax.spines.values():
                spine.set_color(fg_color)
            ax.grid(True, linestyle='--', alpha=0.4, color='#30363d' if dark_mode else '#e0e0e0')
            ax.title.set_color(fg_color)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def clear_all(self):
        """Очистка всех данных"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Очищаем графики
        for ax in self.axes:
            ax.clear()
            ax.set_title("Нет данных", fontsize=12, color="#6c757d")
            ax.axis('off')
        self.canvas.draw()

    def update_table(self, history: pd.DataFrame):
        if history.empty or history.shape[0] == 0:
            self.clear_all()
            return

        stats = history.groupby("nick").agg(
            matches=("nick", "count"),  # ← вот здесь было главное
            total_damage=("damage", "sum"),
            total_heal=("heal", "sum"),
            total_tank=("tank", "sum"),
            total_kills=("kills", "sum"),
            total_efficiency=("efficiency", "sum")
        ).reset_index()

        stats["matches"] = stats["matches"].astype(int)

        stats["avg_damage"] = stats["total_damage"] / stats["matches"].replace(0, 1)
        stats["avg_heal"] = stats["total_heal"] / stats["matches"].replace(0, 1)
        stats["avg_tank"] = stats["total_tank"] / stats["matches"].replace(0, 1)
        stats["avg_efficiency"] = stats["total_efficiency"] / stats["matches"].replace(0, 1)

        stats = stats.sort_values("avg_efficiency", ascending=False)

        self.tree_data = stats.to_dict("records")
        self.update_table_from_sorted_data()

    def update_table_from_sorted_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for rank, row in enumerate(self.tree_data, 1):
            values = (
                rank,
                row["nick"],
                int(row["matches"]),  # ← теперь точно int
                DataProcessor.format_number(row['avg_damage']),
                DataProcessor.format_number(row['avg_heal']),
                DataProcessor.format_number(row['avg_tank']),
                DataProcessor.format_number(row['avg_efficiency'])
            )
            self.tree.insert("", "end", values=values)

        # Зебра + топ-3 (оставляем как было)
        dark = self.main_window.theme['dark']
        even_bg = "#1e252e" if dark else "#f0f0f0"
        odd_bg = "#161b22" if dark else "#ffffff"

        for i, item in enumerate(self.tree.get_children()):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.item(item, tags=(tag,))

        colors = ["#ffcc00", "#c0c0c0", "#cd7f32"]
        for i in range(min(3, len(self.tree.get_children()))):
            item = self.tree.get_children()[i]
            tags = list(self.tree.item(item)["tags"]) + [f"top_{i + 1}"]
            self.tree.item(item, tags=tags)

        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)
        for i, color in enumerate(colors, 1):
            self.tree.tag_configure(f"top_{i}", background=color, font=("Arial", 10, "bold"))

    def update_charts(self, history: pd.DataFrame):
        if history.empty:
            return
        stats = history.groupby("nick").agg({
            "damage": "sum",
            "heal": "sum",
            "tank": "sum"
        }).reset_index()
        dark_mode = self.main_window.theme['dark']
        bg_color = '#0d1117' if dark_mode else '#ffffff'
        fg_color = '#e6edf3' if dark_mode else '#000000'
        metrics = [
            ("damage", "Топ-10 по урону", "Reds"),
            ("heal", "Топ-10 по хилу", "Greens"),
            ("tank", "Топ-10 по танкованию", "Blues")
        ]
        for i, (metric, title, cmap) in enumerate(metrics):
            ax = self.axes[i]
            ax.clear()
            ax.set_facecolor(bg_color)
            ax.title.set_color(fg_color)
            top_players = stats.nlargest(10, metric)
            if top_players.empty or top_players[metric].sum() == 0:
                ax.set_title(f"Нет данных для\n{title}", fontsize=10, fontweight='bold', color=fg_color)
                ax.axis('off')
                continue
            values = top_players[metric].values
            labels = top_players["nick"].values
            mask = values > 0
            values = values[mask]
            labels = labels[mask]
            if len(values) == 0:
                ax.set_title(f"Нет данных для\n{title}", fontsize=10, fontweight='bold', color=fg_color)
                ax.axis('off')
                continue
            colors = plt.get_cmap(cmap)(np.linspace(0.3, 0.9, len(values)))
            wedges, texts = ax.pie(
                values,
                colors=colors,
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1}
            )
            legend_labels = [f"{label}: {int(value):,}" for label, value in zip(labels, values)]
            legend = ax.legend(
                wedges, legend_labels,
                title=title,
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=9,
                frameon=True,
                shadow=True
            )
            legend.get_frame().set_facecolor(bg_color)
            legend.get_frame().set_edgecolor(fg_color)
            for text in legend.get_texts():
                text.set_color(fg_color)
            legend.get_title().set_color(fg_color)
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20, color=fg_color)
        plt.tight_layout(pad=3.0)
        self.canvas.draw()