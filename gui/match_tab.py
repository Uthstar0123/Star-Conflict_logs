import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.data_processor import DataProcessor
from utils.config import ConfigManager


class MatchTab:
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self.ax2 = None
        self.last_df = None

        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill="both", expand=True, padx=6, pady=6)

        self.tree_frame = ttk.Frame(self.paned)
        self.chart_frame = ttk.Frame(self.paned)

        self.setup_treeview()
        self.setup_chart()

        self.paned.add(self.tree_frame, weight=1)
        self.paned.add(self.chart_frame, weight=1)

        self.columns = ("nick", "damage", "self_heal", "team_heal", "tank", "kills", "efficiency")

    def update(self, df: pd.DataFrame):
        self.last_df = None if df is None else df.copy()
        if df is None or df.empty:
            self.clear_all()
            return

        self.update_treeview(df)
        self.update_chart(df)

    def setup_treeview(self):
        header = ttk.Label(
            self.tree_frame,
            text="Разбор последнего матча",
            style="Section.TLabel",
            anchor="center",
        )
        header.pack(fill="x", pady=6)

        columns = ("nick", "damage", "self_heal", "team_heal", "tank", "kills", "efficiency")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=11)

        headings = {
            "nick": "Игрок",
            "damage": "Урон",
            "self_heal": "Самохил",
            "team_heal": "Хил союзников",
            "tank": "Танк",
            "kills": "Фраги",
            "efficiency": "Эффективность",
        }

        widths = {
            "nick": 180,
            "damage": 120,
            "self_heal": 120,
            "team_heal": 130,
            "tank": 120,
            "kills": 80,
            "efficiency": 140,
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        self._sort_reverse = {}
        self.tree.tag_configure("even", background="#1e2936")
        self.tree.tag_configure("odd", background="#15202c")
        self.tree.tag_configure("current_player", background="#1f3b2d", font=("Bahnschrift", 10, "bold"))
        self.tree.tag_configure("cheater", foreground="#ff8b94")

    def sort_by_column(self, col):
        if not hasattr(self, "_sort_reverse"):
            self._sort_reverse = {}
        self._sort_reverse[col] = not self._sort_reverse.get(col, False)
        reverse = self._sort_reverse[col]

        items = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]

        if col in ["damage", "self_heal", "team_heal", "tank", "efficiency"]:
            items.sort(key=lambda x: DataProcessor.parse_number(x[0]), reverse=reverse)
        elif col == "kills":
            items.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0, reverse=reverse)
        else:
            items.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)

        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

    def setup_chart(self):
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, "figure"):
            plt.close(self.figure)

        self.figure = plt.figure(figsize=(10.5, 4.3))
        self.ax = self.figure.add_subplot(111)
        self.ax2 = None

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

    def apply_theme(self):
        self.setup_chart()
        if self.last_df is not None and not self.last_df.empty:
            self.update_treeview(self.last_df)
            self.update_chart(self.last_df)

    def clear_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.ax2:
            self.ax2.remove()
            self.ax2 = None
        self.ax.clear()
        self.ax.set_title("Нет данных для отображения", fontsize=12, color="#6c7a89")
        self.ax.axis("off")
        self.canvas.draw()

    def update_treeview(self, df: pd.DataFrame):
        for item in self.tree.get_children():
            self.tree.delete(item)

        config = ConfigManager.load()
        current_nick = config.get("nick", "").strip().lower()

        dark = self.main_window.theme["dark"]
        even_bg = "#1e2936" if dark else "#f3f6fa"
        odd_bg = "#15202c" if dark else "#ffffff"
        cur_bg = "#1f3b2d" if dark else "#d9f5e9"

        for idx, (_, row) in enumerate(df.iterrows()):
            nick = str(row.get("nick", ""))
            cheat_lvl = int(row.get("cheat_lvl", 0) or 0)
            effective_efficiency = float(row.get("efficiency", 0))
            if cheat_lvl > 0:
                effective_efficiency *= 0.5

            row_id = self.tree.insert(
                "",
                "end",
                values=(
                    nick,
                    DataProcessor.format_number(row.get("damage", 0)),
                    DataProcessor.format_number(row.get("self_heal", 0)),
                    DataProcessor.format_number(row.get("team_heal", 0)),
                    DataProcessor.format_number(row.get("tank", 0)),
                    int(row.get("kills", 0) or 0),
                    DataProcessor.format_number(effective_efficiency),
                ),
            )

            tags = ["even" if idx % 2 == 0 else "odd"]
            if nick.strip().lower() == current_nick and current_nick:
                tags.append("current_player")
            if cheat_lvl > 0:
                tags.append("cheater")
            self.tree.item(row_id, tags=tags)

        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)
        self.tree.tag_configure("current_player", background=cur_bg, font=("Bahnschrift", 10, "bold"))

    def show_cheat_banner(self, cheaters: list, max_lvl: int):
        if not cheaters:
            return

        cheaters_str = ", ".join(cheaters[:5])
        if len(cheaters) > 5:
            cheaters_str += f" и ещё {len(cheaters) - 5}"

        msg = (
            "Обнаружены игроки с аномальным уровнем KPM-теста.\n\n"
            f"Игроки: {cheaters_str}\n"
            f"Максимальный уровень: {max_lvl}\n\n"
            "Их вклад автоматически снижен в 2 раза для честного сравнения."
        )

        messagebox.showwarning("Предупреждение о возможном чит-уровне", msg)

    def update_chart(self, df: pd.DataFrame):
        self.ax.clear()
        if self.ax2 is not None:
            self.ax2.remove()
            self.ax2 = None

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

        if df.empty:
            self.ax.set_title("Нет данных для отображения", fontsize=12, color=fg_color)
            self.canvas.draw()
            return

        players = df["nick"].astype(str).tolist()
        damage = pd.to_numeric(df.get("damage", 0), errors="coerce").fillna(0).values
        self_heal = pd.to_numeric(df.get("self_heal", 0), errors="coerce").fillna(0)
        team_heal = pd.to_numeric(df.get("team_heal", 0), errors="coerce").fillna(0)
        total_heal = (self_heal + team_heal).values
        tank = pd.to_numeric(df.get("tank", 0), errors="coerce").fillna(0).values
        efficiency = pd.to_numeric(df.get("efficiency", 0), errors="coerce").fillna(0).values

        x = range(len(players))
        width = 0.24

        self.ax.bar([i - width for i in x], damage, width, label="Урон", color="#ef5b5b")
        self.ax.bar([i for i in x], total_heal, width, label="Хил", color="#2bbf7f")
        self.ax.bar([i + width for i in x], tank, width, label="Танк", color="#3f8efc")

        self.ax2 = self.ax.twinx()
        self.ax2.plot(x, efficiency, "o-", linewidth=2, color="#f4b740", label="Эффективность")
        self.ax2.set_ylabel("Эффективность", color="#f4b740")
        self.ax2.tick_params(axis="y", labelcolor="#f4b740")
        self.ax2.yaxis.label.set_color("#f4b740")

        self.ax.set_xlabel("Игроки", color=fg_color)
        self.ax.set_ylabel("Значения", color=fg_color)
        self.ax.set_title("Статистика матча", fontsize=14, fontweight="bold", color=fg_color)
        self.ax.set_xticks(list(x))
        self.ax.set_xticklabels(players, rotation=15, ha="right", color=fg_color)

        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        legend = self.ax.legend(lines1 + lines2, labels1 + labels2, loc="best", fontsize=9)
        for text in legend.get_texts():
            text.set_color(fg_color)

        self.figure.tight_layout()
        self.canvas.draw()
