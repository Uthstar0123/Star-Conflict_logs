import pandas as pd

# core/data_processor.py
import pandas as pd

class DataProcessor:
    COEFFS = {
        "damage": 1.0,
        "self_heal": 0.1,
        "team_heal": 2.5,
        "tank": 0.1,
        "kills": 1.0
    }

    @staticmethod
    def add_efficiency(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        df = df.copy()
        df["efficiency"] = (
            df["damage"] * DataProcessor.COEFFS["damage"] +
            df["self_heal"] * DataProcessor.COEFFS["self_heal"] +
            df["team_heal"] * DataProcessor.COEFFS["team_heal"] +
            df["tank"] * DataProcessor.COEFFS["tank"] +
            df["kills"] * DataProcessor.COEFFS["kills"]
        )
        return df

    @staticmethod
    def format_number(n):
        n = float(n)
        if n < 1000: return str(int(n))
        if n < 1_000_000: return f"{n/1000:.1f}к".rstrip('0').rstrip('.')
        if n < 1_000_000_000: return f"{n/1_000_000:.1f}м".rstrip('0').rstrip('.')
        return f"{n/1_000_000_000:.1f}б".rstrip('0').rstrip('.')

    @staticmethod
    def parse_number(s):
        s = str(s).lower().replace(',', '.').strip()
        if 'к' in s: return float(s.replace('к','')) * 1000
        if 'м' in s: return float(s.replace('м','')) * 1_000_000
        if 'б' in s: return float(s.replace('б','')) * 1_000_000_000
        return float(s or 0)

    @staticmethod
    def filter_by_nick(df: pd.DataFrame, nick: str) -> pd.DataFrame:
        if df.empty or not nick: return pd.DataFrame()
        return df[df["nick"] == nick]