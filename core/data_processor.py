import pandas as pd


class DataProcessor:
    COEFFS = {
        "damage": 1.0,
        "self_heal": 0.1,
        "team_heal": 2.5,
        "tank": 0.1,
        "kills": 1.0,
    }
    REQUIRED_COLUMNS = ("damage", "self_heal", "team_heal", "tank", "kills")

    @staticmethod
    def add_efficiency(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        df = df.copy()
        for col in DataProcessor.REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["efficiency"] = (
            df["damage"] * DataProcessor.COEFFS["damage"]
            + df["self_heal"] * DataProcessor.COEFFS["self_heal"]
            + df["team_heal"] * DataProcessor.COEFFS["team_heal"]
            + df["tank"] * DataProcessor.COEFFS["tank"]
            + df["kills"] * DataProcessor.COEFFS["kills"]
        )
        return df

    @staticmethod
    def format_number(n):
        try:
            n = float(n)
        except (TypeError, ValueError):
            n = 0.0

        abs_n = abs(n)
        if abs_n < 1000:
            return str(int(round(n)))
        if abs_n < 1_000_000:
            return f"{n / 1000:.1f}".rstrip("0").rstrip(".") + "k"
        if abs_n < 1_000_000_000:
            return f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".") + "m"
        return f"{n / 1_000_000_000:.1f}".rstrip("0").rstrip(".") + "b"

    @staticmethod
    def parse_number(s):
        if s is None:
            return 0.0

        value = str(s).lower().replace(",", ".").replace(" ", "").strip()
        suffix_map = {
            "к": 1_000,
            "k": 1_000,
            "м": 1_000_000,
            "m": 1_000_000,
            "б": 1_000_000_000,
            "b": 1_000_000_000,
        }

        for suffix, multiplier in suffix_map.items():
            if value.endswith(suffix):
                number = value[:-1] or "0"
                try:
                    return float(number) * multiplier
                except ValueError:
                    return 0.0

        try:
            return float(value or 0)
        except ValueError:
            return 0.0

    @staticmethod
    def filter_by_nick(df: pd.DataFrame, nick: str) -> pd.DataFrame:
        if df.empty or not nick:
            return pd.DataFrame()
        return df[df["nick"] == nick]
