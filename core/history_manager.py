import os
import pandas as pd


class HistoryManager:
    HISTORY_FILE = "history.json"
    EXPECTED_COLUMNS = [
        "nick",
        "damage",
        "self_heal",
        "team_heal",
        "tank",
        "kills",
        "cheat_lvl",
        "efficiency",
        "match_date",
    ]
    NUMERIC_COLUMNS = [
        "damage",
        "self_heal",
        "team_heal",
        "tank",
        "kills",
        "cheat_lvl",
        "efficiency",
    ]

    @staticmethod
    def _normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
        if df is None:
            return pd.DataFrame(columns=HistoryManager.EXPECTED_COLUMNS)

        df = df.copy()

        # Compatibility with old schema where only total heal was stored.
        if "heal" in df.columns and "self_heal" not in df.columns:
            df["self_heal"] = pd.to_numeric(df["heal"], errors="coerce").fillna(0)
        if "team_heal" not in df.columns:
            df["team_heal"] = 0

        for col in HistoryManager.EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = 0 if col != "match_date" else ""

        for col in HistoryManager.NUMERIC_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["nick"] = df["nick"].fillna("").astype(str).str.strip()
        df["match_date"] = df["match_date"].fillna("").astype(str).str.strip()
        df = df[df["nick"] != ""]
        df = df[HistoryManager.EXPECTED_COLUMNS]
        df = df.drop_duplicates(subset=["match_date", "nick"], keep="last")
        return df

    @staticmethod
    def load() -> pd.DataFrame:
        if os.path.exists(HistoryManager.HISTORY_FILE):
            try:
                raw = pd.read_json(HistoryManager.HISTORY_FILE)
                normalized = HistoryManager._normalize_schema(raw)

                # Auto-fix broken/duplicated history on read to stop endless growth.
                needs_rewrite = (
                    len(raw) != len(normalized)
                    or list(raw.columns) != HistoryManager.EXPECTED_COLUMNS
                )
                if needs_rewrite and not normalized.empty:
                    normalized.tail(500).to_json(
                        HistoryManager.HISTORY_FILE,
                        orient="records",
                        force_ascii=False,
                        indent=2,
                    )
                return normalized
            except Exception as e:
                print(f"Ошибка загрузки истории: {e}")

        return pd.DataFrame(columns=HistoryManager.EXPECTED_COLUMNS)

    @staticmethod
    def save_all(df: pd.DataFrame):
        if df is None or df.empty:
            return

        normalized = HistoryManager._normalize_schema(df)
        normalized.tail(500).to_json(
            HistoryManager.HISTORY_FILE,
            orient="records",
            force_ascii=False,
            indent=2,
        )
