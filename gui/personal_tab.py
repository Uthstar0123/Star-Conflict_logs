# gui/personal_tab.py
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk

from core.data_processor import DataProcessor


class PersonalTab:
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        self.stats_frame = ttk.Frame(self.paned)
        self.setup_stats_section()

        self.chart_frame = ttk.Frame(self.paned)
        self.setup_chart()

        self.paned.add(self.stats_frame, weight=1)
        self.paned.add(self.chart_frame, weight=1)

        self.nick = ""
        self.match_data = None

    def setup_stats_section(self):
        header = ttk.Label(self.stats_frame, text="Личная статистика", font=("Arial", 11, "bold"), anchor="center")
        header.pack(fill="x", pady=5)

        stats_container = ttk.Frame(self.stats_frame)
        self.stats_labels = {}

        stats = [
            ("Всего матчей:", "total_matches"),
            ("Средний урон:", "avg_damage"),
            ("Средний самохил:", "avg_self_heal"),
            ("Средний исцеление союзников:", "avg_team_heal"),
            ("Средний танк:", "avg_tank"),
            ("Средняя эффективность:", "avg_efficiency"),
            ("Последний матч:", "last_match")
        ]

        for i, (label_text, var_name) in enumerate(stats):
            ttk.Label(stats_container, text=label_text, font=("Arial", 10)).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            label = ttk.Label(stats_container, text="0", font=("Arial", 10, "bold"))
            label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.stats_labels[var_name] = label

        stats_container.pack(pady=10)

    def setup_chart(self):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, 'figure'):
            plt.close(self.figure)

        self.figure = plt.figure(figsize=(10, 4))
        self.ax = self.figure.add_subplot(111)

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

    def update(self, nick: str, match_data: pd.DataFrame):
        self.nick = nick
        self.match_data = match_data
        if match_data.empty:
            self.clear_all()
            return
        self.update_stats(match_data)
        self.update_chart(match_data)

    def apply_theme(self):
        self.setup_chart()
        if self.match_data is not None:
            self.update_chart(self.match_data)
            self.update_stats(self.match_data)

    def clear_all(self):
        for label in self.stats_labels.values():
            label.config(text="Нет данных")

        self.ax.clear()
        self.ax.set_title(f"Нет данных для игрока {self.nick}", fontsize=12, color="#6c757d")
        self.ax.axis('off')
        self.canvas.draw()

    def update_stats(self, df: pd.DataFrame):
        if df.empty:
            for label in self.stats_labels.values():
                label.config(text="Нет данных")
            return

        total_matches = df["match_date"].nunique()
        if total_matches == 0:
            for label in self.stats_labels.values():
                label.config(text="0")
            return

        total_damage = df["damage"].sum()
        total_self_heal = df.get("self_heal", 0).sum()
        total_team_heal = df.get("team_heal", 0).sum()
        total_tank = df["tank"].sum()
        total_efficiency = df["efficiency"].sum()

        avg_damage = DataProcessor.parse_number(DataProcessor.format_number(total_damage / total_matches))
        avg_self_heal = DataProcessor.parse_number(DataProcessor.format_number(total_self_heal / total_matches))
        avg_team_heal = DataProcessor.parse_number(DataProcessor.format_number(total_team_heal / total_matches))
        avg_tank = DataProcessor.parse_number(DataProcessor.format_number(total_tank / total_matches))
        avg_efficiency = DataProcessor.parse_number(DataProcessor.format_number(total_efficiency / total_matches))

        last_match = df["match_date"].max() if "match_date" in df.columns else "—"

        self.stats_labels["total_matches"].config(text=str(total_matches))
        self.stats_labels["avg_damage"].config(text=f"{avg_damage:.1f}")
        self.stats_labels["avg_self_heal"].config(text=f"{avg_self_heal:.1f}")
        self.stats_labels["avg_team_heal"].config(text=f"{avg_team_heal:.1f}")
        self.stats_labels["avg_tank"].config(text=f"{avg_tank:.1f}")
        self.stats_labels["avg_efficiency"].config(text=f"{avg_efficiency:.1f}")
        self.stats_labels["last_match"].config(text=last_match)

    def update_chart(self, df: pd.DataFrame):
        self.ax.clear()

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

        if df.empty or len(df) < 2:
            self.ax.set_title(f"Недостаточно данных для графика ({self.nick})", fontsize=12, color=fg_color)
            self.canvas.draw()
            return

        plot_data = df.tail(20).copy().reset_index(drop=True)

        self.ax.plot(plot_data.index, plot_data["damage"], 'o-', label='Урон', color='#e74c3c', linewidth=2)
        self.ax.plot(plot_data.index, (plot_data.get("self_heal", 0) + plot_data.get("team_heal", 0)), 'o-', label='Все исцеление', color='#2ecc71', linewidth=2)
        self.ax.plot(plot_data.index, plot_data["tank"], 'o-', label='Танк', color='#3498db', linewidth=2)

        self.ax.set_title(f"Прогресс за последние {len(plot_data)} матчей", fontsize=14, fontweight='bold', color=fg_color)
        self.ax.set_xlabel('Номер матча', color=fg_color)
        self.ax.set_ylabel('Значения', color=fg_color)

        legend = self.ax.legend(loc='best', fontsize=9)
        for text in legend.get_texts():
            text.set_color(fg_color)

        for idx, row in plot_data.iterrows():
            if row["damage"] > 0:
                self.ax.annotate(f'{int(row["damage"])}', (idx, row["damage"]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color=fg_color)
            total_heal = row.get("self_heal", 0) + row.get("team_heal", 0)
            if total_heal > 0:
                self.ax.annotate(f'{int(total_heal)}', (idx, total_heal), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=8, color=fg_color)

        self.figure.tight_layout()
        self.canvas.draw()