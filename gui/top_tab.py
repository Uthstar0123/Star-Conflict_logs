import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.data_processor import DataProcessor


class TopTab:
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill="both", expand=True, padx=6, pady=6)

        self.table_frame = ttk.Frame(self.paned)
        self.chart_frame = ttk.Frame(self.paned)

        self.setup_table()
        self.setup_chart()

        self.paned.add(self.table_frame, weight=1)
        self.paned.add(self.chart_frame, weight=1)

        self.tree_data = []
        self.last_history = None

    def update(self, match_data: pd.DataFrame = None):
        self.last_history = match_data
        if match_data is None or match_data.empty:
            self.clear_all()
            return
        self.update_table(match_data)
        self.update_charts(match_data)

    def apply_theme(self):
        self.setup_chart()
        if self.last_history is not None and not self.last_history.empty:
            self.update_charts(self.last_history)
            self.update_table(self.last_history)

    def setup_table(self):
        header = ttk.Label(
            self.table_frame,
            text="Рейтинг игроков по средней эффективности",
            style="Section.TLabel",
            anchor="center",
        )
        header.pack(fill="x", pady=6)

        columns = ("rank", "nick", "matches", "avg_damage", "avg_heal", "avg_tank", "avg_efficiency")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=16)

        headings = {
            "rank": "Место",
            "nick": "Игрок",
            "matches": "Матчей",
            "avg_damage": "Ср. урон",
            "avg_heal": "Ср. хил",
            "avg_tank": "Ср. танк",
            "avg_efficiency": "Ср. эффективность",
        }

        widths = {
            "rank": 70,
            "nick": 180,
            "matches": 90,
            "avg_damage": 120,
            "avg_heal": 120,
            "avg_tank": 120,
            "avg_efficiency": 160,
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    def sort_by_column(self, col):
        if not hasattr(self, "_sort_reverse"):
            self._sort_reverse = {}
        self._sort_reverse[col] = not self._sort_reverse.get(col, False)
        reverse = self._sort_reverse[col]

        items = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]

        if col == "rank":
            items.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 999, reverse=reverse)
        elif col in ["avg_damage", "avg_heal", "avg_tank", "avg_efficiency"]:
            items.sort(key=lambda x: DataProcessor.parse_number(x[0]), reverse=reverse)
        elif col == "matches":
            items.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0, reverse=reverse)
        else:
            items.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)

        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

        self.tree.update_idletasks()

    def setup_chart(self):
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, "figure"):
            plt.close(self.figure)

        self.figure, self.axes = plt.subplots(1, 3, figsize=(13, 4.2))

        dark_mode = self.main_window.theme["dark"]
        bg_color = self.main_window.theme["bg"] if dark_mode else "#ffffff"
        fg_color = self.main_window.theme["fg"]

        self.figure.patch.set_facecolor(bg_color)

        for ax in self.axes:
            ax.set_facecolor(bg_color)
            ax.tick_params(colors=fg_color)
            for spine in ax.spines.values():
                spine.set_color(fg_color)
            ax.grid(True, linestyle="--", alpha=0.25, axis="x", color=self.main_window.theme["panel"])
            ax.title.set_color(fg_color)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

    def clear_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for ax in self.axes:
            ax.clear()
            ax.set_title("Нет данных", fontsize=12, color="#6c7a89")
            ax.axis("off")
        self.canvas.draw()

    def update_table(self, history: pd.DataFrame):
        if history is None or history.empty:
            self.clear_all()
            return

        numeric_cols = ["damage", "self_heal", "team_heal", "tank", "efficiency"]
        history = history.copy()
        if "match_date" in history.columns:
            history = history.drop_duplicates(subset=["match_date", "nick"], keep="last")

        for col in numeric_cols:
            if col not in history.columns:
                history[col] = 0
            history[col] = pd.to_numeric(history[col], errors="coerce").fillna(0)

        stats = (
            history.groupby("nick")
            .agg(
                matches=("nick", "count"),
                total_damage=("damage", "sum"),
                total_self=("self_heal", "sum"),
                total_team=("team_heal", "sum"),
                total_tank=("tank", "sum"),
                total_efficiency=("efficiency", "sum"),
            )
            .reset_index()
        )

        stats["matches"] = stats["matches"].astype(int)
        safe_matches = stats["matches"].replace(0, 1)
        stats["avg_damage"] = stats["total_damage"] / safe_matches
        stats["avg_heal"] = (stats["total_self"] + stats["total_team"]) / safe_matches
        stats["avg_tank"] = stats["total_tank"] / safe_matches
        stats["avg_efficiency"] = stats["total_efficiency"] / safe_matches

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
                int(row["matches"]),
                DataProcessor.format_number(row["avg_damage"]),
                DataProcessor.format_number(row["avg_heal"]),
                DataProcessor.format_number(row["avg_tank"]),
                DataProcessor.format_number(row["avg_efficiency"]),
            )
            self.tree.insert("", "end", values=values)

        dark = self.main_window.theme["dark"]
        even_bg = "#1e2936" if dark else "#f3f6fa"
        odd_bg = "#15202c" if dark else "#ffffff"

        for i, item in enumerate(self.tree.get_children()):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.item(item, tags=(tag,))

        top_colors = ["#f7c948", "#c5ced8", "#d79c6b"]
        for i in range(min(3, len(self.tree.get_children()))):
            item = self.tree.get_children()[i]
            tags = list(self.tree.item(item)["tags"]) + [f"top_{i + 1}"]
            self.tree.item(item, tags=tags)

        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)
        for i, color in enumerate(top_colors, 1):
            self.tree.tag_configure(f"top_{i}", background=color, font=("Bahnschrift", 10, "bold"))

    def update_charts(self, history: pd.DataFrame):
        if history is None or history.empty:
            return

        safe_history = history.copy()
        if "match_date" in safe_history.columns:
            safe_history = safe_history.drop_duplicates(subset=["match_date", "nick"], keep="last")

        stats = safe_history.groupby("nick").agg({
            "damage": "sum",
            "self_heal": "sum",
            "team_heal": "sum",
            "tank": "sum",
        }).reset_index()

        stats["heal"] = pd.to_numeric(stats["self_heal"], errors="coerce").fillna(0) + pd.to_numeric(
            stats["team_heal"], errors="coerce"
        ).fillna(0)

        dark_mode = self.main_window.theme["dark"]
        bg_color = self.main_window.theme["bg"] if dark_mode else "#ffffff"
        fg_color = self.main_window.theme["fg"]

        metrics = [
            ("damage", "Топ-10 по урону", "#ef5b5b"),
            ("heal", "Топ-10 по хилу", "#2bbf7f"),
            ("tank", "Топ-10 по танку", "#3f8efc"),
        ]

        for i, (metric, title, color) in enumerate(metrics):
            ax = self.axes[i]
            ax.clear()
            ax.set_facecolor(bg_color)
            ax.tick_params(colors=fg_color)
            for spine in ax.spines.values():
                spine.set_color(fg_color)

            top_players = stats.nlargest(10, metric).sort_values(metric)
            top_players = top_players[top_players[metric] > 0]

            if top_players.empty:
                ax.set_title(f"Нет данных для {title.lower()}", fontsize=10, color=fg_color)
                ax.axis("off")
                continue

            labels = []
            for nick in top_players["nick"].astype(str).tolist():
                labels.append(nick if len(nick) <= 12 else f"{nick[:11]}…")
            values = top_players[metric].astype(float).tolist()

            ax.barh(labels, values, color=color, alpha=0.9)
            ax.set_title(title, fontsize=12, fontweight="bold", color=fg_color)
            ax.tick_params(axis="y", labelsize=9, colors=fg_color)

            max_val = max(values) if values else 0
            ax.set_xlim(0, max_val * 1.22 if max_val else 1)
            for y, value in enumerate(values):
                # Keep value labels inside axes so they do not overflow outside charts.
                x_pos = min(value + max_val * 0.02, max_val * 1.18) if max_val else value
                ax.text(
                    x_pos,
                    y,
                    DataProcessor.format_number(value),
                    va="center",
                    fontsize=8,
                    color=fg_color,
                    clip_on=True,
                )

        self.figure.tight_layout(pad=1.8, rect=(0.02, 0.04, 0.98, 0.98))
        self.canvas.draw()
