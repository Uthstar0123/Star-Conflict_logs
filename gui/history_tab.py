import tkinter as tk
from tkinter import ttk

import pandas as pd

from core.history_manager import HistoryManager


class HistoryTab:
    def __init__(self, parent, on_match_selected):
        self.frame = ttk.Frame(parent)
        self.on_match_selected = on_match_selected

        columns = ("match_id", "date", "players")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=15)

        self.tree.heading("match_id", text="ID")
        self.tree.heading("date", text="Дата матча")
        self.tree.heading("players", text="Игроки")

        self.tree.column("match_id", width=50, anchor="center")
        self.tree.column("date", width=220, anchor="center")
        self.tree.column("players", width=520, anchor="w")

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<Double-1>", self._on_match_select)
        self.load_matches()

    def load_matches(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        history = HistoryManager.load()
        if history.empty or "match_date" not in history.columns:
            self.tree.insert("", "end", values=("-", "История пуста", ""))
            return
        history = history.drop_duplicates(subset=["match_date", "nick"], keep="last")

        unique_dates = history["match_date"].dropna().astype(str).unique().tolist()
        unique_dates.sort(reverse=True)

        if not unique_dates:
            self.tree.insert("", "end", values=("-", "История пуста", ""))
            return

        for i, date in enumerate(unique_dates[:50], 1):
            match_players = history[history["match_date"] == date]["nick"].dropna().astype(str).unique().tolist()
            preview_players = match_players[:6]
            players_str = ", ".join(preview_players)
            if len(match_players) > 6:
                players_str += f" и ещё {len(match_players) - 6}"
            self.tree.insert("", "end", values=(i, date, players_str))

    def _on_match_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        match_date = item["values"][1]
        if match_date == "История пуста":
            return

        history = HistoryManager.load()
        match_data = history[history["match_date"] == match_date]
        self.on_match_selected(match_data)
