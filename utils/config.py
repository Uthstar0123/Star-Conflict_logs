# utils/config.py
import json
import os

class ConfigManager:
    CONFIG_FILE = "config.json"

    @staticmethod
    def load() -> dict:
        if os.path.exists(ConfigManager.CONFIG_FILE):
            with open(ConfigManager.CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Значения по умолчанию, если ключей нет
                data.setdefault("nick", "")
                data.setdefault("log_dir", "")
                data.setdefault("dark_theme", True)
                data.setdefault("alpha", 0.92)
                return data
        return {
            "nick": "",
            "log_dir": "",
            "dark_theme": True,
            "alpha": 0.92
        }

    @staticmethod
    def save(nick: str = None, log_dir: str = None, dark_theme: bool = None, alpha: float = None):
        data = ConfigManager.load()
        if nick is not None:
            data["nick"] = nick
        if log_dir is not None:
            data["log_dir"] = log_dir
        if dark_theme is not None:
            data["dark_theme"] = dark_theme
        if alpha is not None:
            data["alpha"] = alpha
        with open(ConfigManager.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)