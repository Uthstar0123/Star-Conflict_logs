# gui/history_tab.py
import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
from core.history_manager import HistoryManager


class HistoryTab:
    def __init__(self, parent, on_match_selected):
        self.frame = ttk.Frame(parent)
        self.on_match_selected = on_match_selected

        # Создаём Treeview для списка матчей
        columns = ("match_id", "date", "players")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=15)

        self.tree.heading("match_id", text="ID")
        self.tree.heading("date", text="Дата матча")
        self.tree.heading("players", text="Игроки")

        self.tree.column("match_id", width=50, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("players", width=300, anchor="w")

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Обработчик двойного клика
        self.tree.bind("<Double-1>", self._on_match_select)

        self.load_matches()

    @staticmethod
    def load() -> pd.DataFrame:
        if os.path.exists(HistoryManager.HISTORY_FILE):
            try:
                df = pd.read_json(HistoryManager.HISTORY_FILE)
                expected_cols = ["nick", "damage", "self_heal", "team_heal", "tank", "kills", "efficiency", "match_date"]
                for col in expected_cols:
                    if col not in df.columns:
                        df[col] = 0 if col != "match_date" else ""
                return df
            except Exception as e:
                print(f"Ошибка загрузки истории: {e}")
        return pd.DataFrame(columns=["nick", "damage", "self_heal", "team_heal", "tank", "kills", "efficiency", "match_date"])

    def load_matches(self):
        history = HistoryManager.load()
        if history.empty:
            return

        # Группируем по дате матча (уникальные бои)
        unique_dates = history["match_date"].dropna().unique()
        # Сортируем от новых к старым
        unique_dates = sorted(unique_dates, reverse=True)

        for i, date in enumerate(unique_dates[:20], 1):  # последние 20 матчей
            match_players = history[history["match_date"] == date]["nick"].unique()
            players_str = ", ".join(match_players[:5])  # первые 5 игроков
            self.tree.insert("", "end", values=(i, date, players_str))

    def _on_match_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        match_date = item["values"][1]

        # Загружаем данные именно этого матча
        history = HistoryManager.load()
        match_data = history[history["match_date"] == match_date]

        self.on_match_selected(match_data)