# core/history_manager.py
import pandas as pd
import os

class HistoryManager:
    HISTORY_FILE = "history.json"

    @staticmethod
    # core/history_manager.py
    def load() -> pd.DataFrame:
        if os.path.exists(HistoryManager.HISTORY_FILE):
            try:
                df = pd.read_json(HistoryManager.HISTORY_FILE)
                # Теперь ожидаем efficiency в колонках
                expected_cols = ["nick", "damage", "self_heal", "team_heal", "tank", "kills", "efficiency", "match_date"]
                for col in expected_cols:
                    if col not in df.columns:
                        df[col] = 0 if col != "match_date" else ""
                return df
            except Exception as e:
                print(f"Ошибка загрузки истории: {e}")
        return pd.DataFrame(columns=["nick", "damage", "heal", "tank", "kills", "efficiency", "match_date"])

    @staticmethod
    def save_all(df: pd.DataFrame):
        if df.empty:
            return
        # Сохраняем все матчи (ограничим 200 для скорости)
        df.tail(500).to_json(HistoryManager.HISTORY_FILE, orient="records", force_ascii=False, indent=2)
