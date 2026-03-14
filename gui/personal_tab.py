import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.data_processor import DataProcessor


class PersonalTab:
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill="both", expand=True, padx=6, pady=6)

        self.stats_frame = ttk.Frame(self.paned)
        self.chart_frame = ttk.Frame(self.paned)

        self.setup_stats_section()
        self.setup_chart()

        self.paned.add(self.stats_frame, weight=1)
        self.paned.add(self.chart_frame, weight=1)

        self.nick = ""
        self.match_data = None

    def setup_stats_section(self):
        header = ttk.Label(
            self.stats_frame,
            text="Личная статистика",
            style="Section.TLabel",
            anchor="center",
        )
        header.pack(fill="x", pady=6)

        stats_container = ttk.LabelFrame(self.stats_frame, text="Сводка", padding=12)
        stats_container.pack(fill="x", padx=10, pady=8)
        stats_container.columnconfigure(0, weight=1)

        # Centered grid inside the summary frame.
        stats_grid = ttk.Frame(stats_container)
        stats_grid.grid(row=0, column=0, sticky="n")
        stats_grid.columnconfigure(0, minsize=220)
        stats_grid.columnconfigure(1, minsize=180)

        self.stats_labels = {}
        stats = [
            ("Всего матчей:", "total_matches"),
            ("Средний урон:", "avg_damage"),
            ("Средний самохил:", "avg_self_heal"),
            ("Средний хил союзников:", "avg_team_heal"),
            ("Средний танк:", "avg_tank"),
            ("Средняя эффективность:", "avg_efficiency"),
            ("Последний матч:", "last_match"),
        ]

        for i, (label_text, var_name) in enumerate(stats):
            ttk.Label(stats_grid, text=label_text, anchor="e").grid(row=i, column=0, sticky="e", padx=6, pady=3)
            label = ttk.Label(stats_grid, text="-", style="StatValue.TLabel")
            label.grid(row=i, column=1, sticky="w", padx=6, pady=3)
            self.stats_labels[var_name] = label

    def setup_chart(self):
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, "figure"):
            plt.close(self.figure)

        self.figure = plt.figure(figsize=(10.5, 4.3))
        self.ax = self.figure.add_subplot(111)

        dark_mode = self.main_window.theme["dark"]
        bg_color = self.main_window.theme["bg"] if dark_mode else "#ffffff"
        fg_color = self.main_window.theme["fg"]

        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.tick_params(colors=fg_color)
        for spine in self.ax.spines.values():
            spine.set_color(fg_color)
        self.ax.grid(True, linestyle="--", alpha=0.35, color=self.main_window.theme["panel"])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

    def update(self, nick: str, match_data: pd.DataFrame):
        self.nick = nick
        self.match_data = match_data.copy() if match_data is not None else None

        if match_data is None or match_data.empty:
            self.clear_all()
            return

        self.update_stats(match_data)
        self.update_chart(match_data)

    def apply_theme(self):
        self.setup_chart()
        if self.match_data is not None and not self.match_data.empty:
            self.update_chart(self.match_data)
            self.update_stats(self.match_data)

    def clear_all(self):
        for label in self.stats_labels.values():
            label.config(text="Нет данных")

        self.ax.clear()
        self.ax.set_title(f"Нет данных для игрока {self.nick or '-'}", fontsize=12, color="#6c7a89")
        self.ax.axis("off")
        self.canvas.draw()

    def update_stats(self, df: pd.DataFrame):
        if df.empty:
            self.clear_all()
            return

        safe_df = df.copy()
        if "match_date" in safe_df.columns:
            safe_df = safe_df.drop_duplicates(subset=["match_date", "nick"], keep="last")

        for col in ["damage", "self_heal", "team_heal", "tank", "efficiency"]:
            if col not in safe_df.columns:
                safe_df[col] = 0
            safe_df[col] = pd.to_numeric(safe_df[col], errors="coerce").fillna(0)

        if "match_date" in safe_df.columns:
            total_matches = int(safe_df["match_date"].astype(str).nunique())
            last_match = safe_df["match_date"].astype(str).max()
        else:
            total_matches = len(safe_df)
            last_match = "-"

        total_matches = max(total_matches, 1)

        avg_damage = safe_df["damage"].sum() / total_matches
        avg_self_heal = safe_df["self_heal"].sum() / total_matches
        avg_team_heal = safe_df["team_heal"].sum() / total_matches
        avg_tank = safe_df["tank"].sum() / total_matches
        avg_efficiency = safe_df["efficiency"].sum() / total_matches

        self.stats_labels["total_matches"].config(text=str(total_matches))
        self.stats_labels["avg_damage"].config(text=DataProcessor.format_number(avg_damage))
        self.stats_labels["avg_self_heal"].config(text=DataProcessor.format_number(avg_self_heal))
        self.stats_labels["avg_team_heal"].config(text=DataProcessor.format_number(avg_team_heal))
        self.stats_labels["avg_tank"].config(text=DataProcessor.format_number(avg_tank))
        self.stats_labels["avg_efficiency"].config(text=DataProcessor.format_number(avg_efficiency))
        self.stats_labels["last_match"].config(text=last_match)

    def update_chart(self, df: pd.DataFrame):
        self.ax.clear()

        dark_mode = self.main_window.theme["dark"]
        fg_color = self.main_window.theme["fg"]
        bg_color = self.main_window.theme["bg"] if dark_mode else "#ffffff"

        self.ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)
        self.ax.tick_params(colors=fg_color)
        self.ax.xaxis.label.set_color(fg_color)
        self.ax.yaxis.label.set_color(fg_color)
        self.ax.title.set_color(fg_color)
        for spine in self.ax.spines.values():
            spine.set_color(fg_color)

        safe_df = df.copy()
        if "match_date" in safe_df.columns:
            safe_df = safe_df.drop_duplicates(subset=["match_date", "nick"], keep="last")

        if safe_df.empty or len(safe_df) < 2:
            self.ax.set_title(f"Недостаточно данных для графика ({self.nick})", fontsize=12, color=fg_color)
            self.canvas.draw()
            return

        plot_data = safe_df.tail(20).copy().reset_index(drop=True)
        plot_data["damage"] = pd.to_numeric(plot_data.get("damage", 0), errors="coerce").fillna(0)
        plot_data["self_heal"] = pd.to_numeric(plot_data.get("self_heal", 0), errors="coerce").fillna(0)
        plot_data["team_heal"] = pd.to_numeric(plot_data.get("team_heal", 0), errors="coerce").fillna(0)
        plot_data["tank"] = pd.to_numeric(plot_data.get("tank", 0), errors="coerce").fillna(0)

        x = plot_data.index
        damage = plot_data["damage"]
        heal = plot_data["self_heal"] + plot_data["team_heal"]
        tank = plot_data["tank"]

        self.ax.plot(x, damage, "o-", label="Урон", color="#ef5b5b", linewidth=2)
        self.ax.plot(x, heal, "o-", label="Хил", color="#2bbf7f", linewidth=2)
        self.ax.plot(x, tank, "o-", label="Танк", color="#3f8efc", linewidth=2)

        self.ax.fill_between(x, 0, damage, color="#ef5b5b", alpha=0.08)
        self.ax.fill_between(x, 0, heal, color="#2bbf7f", alpha=0.08)

        self.ax.set_title(
            f"Динамика за последние {len(plot_data)} матчей",
            fontsize=14,
            fontweight="bold",
            color=fg_color,
        )
        self.ax.set_xlabel("Номер матча", color=fg_color)
        self.ax.set_ylabel("Значение", color=fg_color)

        legend = self.ax.legend(loc="best", fontsize=9)
        for text in legend.get_texts():
            text.set_color(fg_color)

        self.figure.tight_layout()
        self.canvas.draw()
