import os
import re
from datetime import datetime
from typing import Dict, List

import pandas as pd


class LogParser:
    PLAYER_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")

    NON_PLAYER_PREFIXES = {
        "ClanShip_",
        "Ship_Bot_",
        "NPC",
        "Module",
        "BP",
        "Swarm",
        "Movement_",
        "Weapon_",
        "Spell_",
        "SpaceShip",
        "Clanship_",
        "Ship_",
        "BtB",
        "VitalPoint_",
        "GuardDrone",
        "Anomaly",
        "Bonus_",
        "GreenBattleStation_",
        "GreenPlatform_",
        "Companion_",
        "GreenBeacon_",
        "Drone_",
        "Turret_",
        "Flak_",
        "Rocket_",
        "Station",
        "Beacon",
        "Platform",
        "Debris",
        "WarpGate",
        "HealBot",
        "n/a",
        "ScenePhysicsEntity",
        "OpenWorld_Empire_EStation01",
        "SpasmicMonkey",
        "Medium_WarpGate",
        "R7Tech",
        "Wreck_R2_L",
        "PlasmaHurt",
        "TStick",
        "Constructor_3_24Monitors",
        "AiAgent",
        "pa1adin4ik",
        "Alien_Scout_Raid",
        "PvE_RaidAvanpost",
        "TestDroidAlien",
        "PvE_RaidRocketTurret",
        "Cruiser_Shield",
        "TurretPlasma_CruiserAlien",
        "Constructor_6_13",
    }

    @staticmethod
    def is_player_name(name: str) -> bool:
        if not name or len(name) < 2 or name == "n/a":
            return False
        if any(name.startswith(prefix) for prefix in LogParser.NON_PLAYER_PREFIXES):
            return False
        return bool(LogParser.PLAYER_REGEX.fullmatch(name))

    @staticmethod
    def is_structure(name: str) -> bool:
        return any(name.startswith(prefix) for prefix in LogParser.NON_PLAYER_PREFIXES)

    @staticmethod
    def _empty_stats() -> Dict:
        return {
            "damage": 0,
            "self_heal": 0,
            "team_heal": 0,
            "tank": 0,
            "kills": 0,
            "cheat_lvl": 0,
            "lives": [],
            "participation": [],
        }

    @staticmethod
    def _parse_lines(lines: List[str]) -> Dict[str, Dict]:
        player_actions: Dict[str, Dict] = {}

        def get_stats(nick: str) -> Dict:
            return player_actions.setdefault(nick, LogParser._empty_stats())

        for i, line in enumerate(lines):
            dmg_match = re.search(
                r"Damage\s+([^\s|]+)(?:\s*\|\S+)?\s*->\s*([^\s|]+)(?:\s*\|\S+)?\s*([\d.]+)\s*\(h:([\d.]+)\s+s:([\d.]+)\)",
                line,
            )
            if dmg_match:
                attacker = dmg_match.group(1).strip()
                target = dmg_match.group(2).strip()
                if "<FriendlyFire>" in line or attacker == target:
                    continue
                if LogParser.is_player_name(attacker) and not LogParser.is_structure(target):
                    try:
                        dmg = int(float(dmg_match.group(3)))
                        tank = int(float(dmg_match.group(5)))
                    except ValueError:
                        continue

                    stats = get_stats(attacker)
                    stats["damage"] += dmg
                    stats["tank"] += tank
                continue

            heal_match = re.search(
                r"Heal\s+([^\s|]+)(?:\s*\|\S+)?\s*->\s*([^\s|]+)(?:\s*\|\S+)?\s*([\d.]+)",
                line,
            )
            if heal_match:
                healer = heal_match.group(1).strip()
                target = heal_match.group(2).strip()
                if LogParser.is_player_name(healer) and not LogParser.is_structure(target):
                    try:
                        heal_val = int(float(heal_match.group(3)))
                    except ValueError:
                        continue

                    stats = get_stats(healer)
                    if healer == target:
                        stats["self_heal"] += heal_val
                    else:
                        stats["team_heal"] += heal_val
                continue

            kill_match = re.search(r"(?:Killed|destroyed)\s+([^\t|]+).*?killer\s+([^\s|]+)", line, re.IGNORECASE)
            if kill_match:
                killer = kill_match.group(2).strip()
                if LogParser.is_player_name(killer):
                    stats = get_stats(killer)
                    stats["kills"] += 1

                    j = i + 1
                    while j < len(lines) and "Participant" in lines[j]:
                        part = re.search(r"Participant '([^']+)' .*?totalDamage (\d+)", lines[j])
                        if part and LogParser.is_player_name(part.group(1)):
                            stats["participation"].append(
                                {"player": part.group(1), "damage": int(part.group(2))}
                            )
                        j += 1

            cheat_match = re.search(r"TestKPMNormalizer_(\d+)", line)
            if cheat_match:
                lvl = int(cheat_match.group(1))
                p_match = re.search(r"by ([^\s]+)", line)
                if p_match and LogParser.is_player_name(p_match.group(1)):
                    nick = p_match.group(1)
                    stats = get_stats(nick)
                    stats["cheat_lvl"] = max(stats.get("cheat_lvl", 0), lvl)

            if "Spawn SpaceShip" in line:
                spawn = re.search(r"Spawn SpaceShip for player\d+ \(([^,]+)", line)
                if spawn and LogParser.is_player_name(spawn.group(1)):
                    nick = spawn.group(1)
                    stats = get_stats(nick)
                    stats["lives"].append({"ship": nick, "start_time": line[:8], "start_idx": i})

            death_match = re.search(r"(Killed|destroyed)\s+([^\t|]+)", line, re.IGNORECASE)
            if death_match:
                victim = death_match.group(2).strip()
                if LogParser.is_player_name(victim) and victim in player_actions:
                    lives = player_actions[victim].get("lives", [])
                    if lives:
                        lives[-1]["end_time"] = line[:8]
                        lives[-1]["end_idx"] = i

        return player_actions

    @staticmethod
    def parse_single_last_match(file_path: str) -> pd.DataFrame:
        if not os.path.exists(file_path):
            return pd.DataFrame()

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        last_start = content.rfind("Start gameplay")
        if last_start == -1:
            return pd.DataFrame()

        lines = content[last_start:].splitlines()
        player_actions = LogParser._parse_lines(lines)

        if not player_actions:
            return pd.DataFrame()

        data = [
            {
                "nick": nick,
                "damage": stats["damage"],
                "self_heal": stats.get("self_heal", 0),
                "team_heal": stats.get("team_heal", 0),
                "tank": stats["tank"],
                "kills": stats["kills"],
                "cheat_lvl": stats.get("cheat_lvl", 0),
            }
            for nick, stats in player_actions.items()
        ]
        return pd.DataFrame(data)

    @staticmethod
    def get_latest_log_dir(log_dir: str) -> str | None:
        if not os.path.exists(log_dir):
            return None

        subdirs = [
            os.path.join(log_dir, d)
            for d in os.listdir(log_dir)
            if os.path.isdir(os.path.join(log_dir, d))
        ]

        valid_dirs = []
        for folder_path in subdirs:
            folder_name = os.path.basename(folder_path)
            try:
                folder_dt = datetime.strptime(folder_name, "%Y.%m.%d %H.%M.%S.%f")
                valid_dirs.append((folder_path, folder_dt))
            except ValueError:
                continue

        if not valid_dirs:
            return None

        return max(valid_dirs, key=lambda x: x[1])[0]

    @staticmethod
    def get_last_match_from_latest_log(log_dir: str) -> pd.DataFrame:
        latest_dir = LogParser.get_latest_log_dir(log_dir)
        if not latest_dir:
            return pd.DataFrame()

        combat_log = os.path.join(latest_dir, "combat.log")
        if not os.path.exists(combat_log):
            return pd.DataFrame()

        df = LogParser.parse_single_last_match(combat_log)
        if not df.empty:
            df["match_date"] = os.path.basename(latest_dir)
        return df

    @staticmethod
    def update_history(new_match: pd.DataFrame):
        from core.data_processor import DataProcessor
        from core.history_manager import HistoryManager

        if new_match is None or new_match.empty:
            return

        history = HistoryManager.load().dropna(how="all")
        new_match = new_match.dropna(how="all").copy()

        if "nick" not in new_match.columns:
            return
        if "match_date" not in new_match.columns:
            new_match["match_date"] = ""

        new_match["nick"] = new_match["nick"].astype(str).str.strip()
        new_match = new_match[new_match["nick"] != ""]
        if new_match.empty:
            return

        if "efficiency" not in new_match.columns:
            new_match = DataProcessor.add_efficiency(new_match)

        key_cols = ["match_date", "nick"]
        new_match = new_match.drop_duplicates(subset=key_cols, keep="last")

        if history.empty:
            updated = new_match
        else:
            updated = pd.concat([history, new_match], ignore_index=True)
            updated = updated.drop_duplicates(subset=key_cols, keep="last")

        HistoryManager.save_all(updated)
