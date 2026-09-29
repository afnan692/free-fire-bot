# -*- coding: utf-8 -*-
"""
FreeFire Level Up Bot - Professional Web Dashboard & Real-Time EXP Tracker
Embedded Async Web Server (aiohttp)
Optimized for ultra-smooth operation, zero memory leaks, and dynamic multi-account control.
"""

import asyncio
import json
import os
import time
import secrets
import hashlib
from typing import Dict, List, Any, Optional
from aiohttp import web

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")
ACCESS_KEYS_FILE = "access_keys.json"
DEFAULT_ADMIN_KEY = "TOXIC2"

EXP_TABLE: Dict[int, int] = {
    1: 0, 2: 48, 3: 202, 4: 544, 5: 1012, 6: 1844, 7: 2792, 8: 3800,
    9: 4870, 10: 6004, 11: 7192, 12: 8448, 13: 9760, 14: 11140, 15: 12566,
    16: 14060, 17: 15610, 18: 17224, 19: 18902, 20: 20632, 21: 22424, 22: 24278,
    23: 26192, 24: 28166, 25: 30200, 26: 32294, 27: 34448, 28: 37804, 29: 41274,
    30: 44870, 31: 48582, 32: 53394, 33: 58566, 34: 64096, 35: 69994, 36: 76460,
    37: 83506, 38: 91128, 39: 99322, 40: 108092, 41: 120144, 42: 133266, 43: 147472,
    44: 162760, 45: 179126, 46: 196572, 47: 215368, 48: 235516, 49: 257010, 50: 279860,
    51: 304056, 52: 348318, 53: 394982, 54: 444044, 55: 495508, 56: 549364, 57: 633756,
    58: 721744, 59: 813336, 60: 908522, 61: 1041438, 62: 1180352, 63: 1325266,
    64: 1476184, 65: 1634300, 66: 1840946, 67: 2056594, 68: 2281242, 69: 2514880,
    70: 2757530, 71: 3059506, 72: 3372284, 73: 3699456, 74: 4041030, 75: 4397002,
    76: 4829104, 77: 5282204, 78: 5756304, 79: 6251408, 80: 6776502, 81: 7381324,
    82: 8043154, 83: 8752982, 84: 9510808, 85: 10316338, 86: 11277190, 87: 12291748,
    88: 13360304, 89: 14482858, 90: 15659418, 91: 17026708, 92: 18453950, 93: 19941280,
    94: 21488570, 95: 23095858, 96: 24763138, 97: 26490428, 98: 28378704, 99: 30124996,
    100: 32032884
}

def calculate_level_progress(level: int, current_exp: int) -> Dict[str, Any]:
    level = max(1, level)
    next_level = min(100, level + 1)
    base_exp = EXP_TABLE.get(level, 0)
    target_exp = EXP_TABLE.get(next_level, base_exp + 50000)
    
    needed_for_level = max(1, target_exp - base_exp)
    earned_in_level = max(0, current_exp - base_exp)
    remaining_exp = max(0, target_exp - current_exp)
    progress_pct = min(100.0, max(0.0, (earned_in_level / needed_for_level) * 100.0))

    return {
        "next_level": next_level,
        "base_exp": base_exp,
        "target_exp": target_exp,
        "needed_for_level": needed_for_level,
        "earned_in_level": earned_in_level,
        "remaining_exp": remaining_exp,
        "progress_pct": round(progress_pct, 1)
    }


# ==================== ACCESS KEY MANAGEMENT ====================
def load_access_keys() -> Dict[str, Dict[str, Any]]:
    """Load access keys from file or create default admin key"""
    if os.path.exists(ACCESS_KEYS_FILE):
        try:
            with open(ACCESS_KEYS_FILE, "r", encoding="utf-8") as f:
                keys = json.load(f)
                if isinstance(keys, dict):
                    return keys
        except Exception:
            pass
    
    # Create default admin key if file doesn't exist
    default_keys = {
        DEFAULT_ADMIN_KEY: {
            "key": DEFAULT_ADMIN_KEY,
            "is_admin": True,
            "created_at": time.time(),
            "created_by": "system",
            "name": "Default Admin"
        }
    }
    save_access_keys(default_keys)
    return default_keys


def save_access_keys(keys: Dict[str, Dict[str, Any]]):
    """Save access keys to file"""
    try:
        with open(ACCESS_KEYS_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2)
    except Exception as e:
        print(f"Error saving access keys: {e}")


def validate_access_key(key: str) -> Optional[Dict[str, Any]]:
    """Validate an access key and return its data if valid"""
    if not key:
        return None
    
    keys = load_access_keys()
    key_data = keys.get(key)
    
    if key_data:
        return key_data
    
    return None


def is_admin_key(key: str) -> bool:
    """Check if a key has admin privileges"""
    key_data = validate_access_key(key)
    return key_data and key_data.get("is_admin", False)


def generate_access_key(prefix: str = "USER") -> str:
    """Generate a random access key"""
    random_part = secrets.token_hex(8).upper()
    return f"{prefix}_{random_part}"


def create_access_key(name: str, is_admin: bool = False, created_by: str = "admin") -> Optional[str]:
    """Create a new access key (admin only)"""
    keys = load_access_keys()
    
    prefix = "ADMIN" if is_admin else "USER"
    new_key = generate_access_key(prefix)
    
    keys[new_key] = {
        "key": new_key,
        "is_admin": is_admin,
        "created_at": time.time(),
        "created_by": created_by,
        "name": name
    }
    
    save_access_keys(keys)
    return new_key


def delete_access_key(key: str, requesting_key: str) -> bool:
    """Delete an access key (admin only, cannot delete default admin)"""
    if not is_admin_key(requesting_key):
        return False
    
    if key == DEFAULT_ADMIN_KEY:
        return False  # Cannot delete default admin key
    
    keys = load_access_keys()
    if key in keys:
        del keys[key]
        save_access_keys(keys)
        return True
    
    return False


def list_access_keys(requesting_key: str) -> List[Dict[str, Any]]:
    """List all access keys (admin only)"""
    if not is_admin_key(requesting_key):
        return []
    
    keys = load_access_keys()
    return list(keys.values())

# Global bot state shared between Main.py and Web Dashboard
class BotState:
    def __init__(self):
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.logs: List[Dict[str, Any]] = []
        self.max_logs = 200
        self.total_matches = 0
        self.total_matches_started = 0      # 🔥 NEW
        self.total_gained_exp = 0
        self.start_time = time.time()
        self.account_workers: Dict[str, asyncio.Task] = {}
        self.account_token_map: Dict[str, str] = {}  # uid -> token or token_prefix -> uid
        self.auth_to_game_id: Dict[str, str] = {}   # guest login uid -> in-game account id
        self.game_to_auth_id: Dict[str, str] = {}   # in-game account id -> guest login uid
        self.paused_accounts: set = set()
        self.refresh_callbacks: Dict[str, Any] = {}
        self.account_credentials: Dict[str, Dict[str, Any]] = {}
        self.active_writers: Dict[str, set] = {}

    def register_writer(self, uid: str, writer):
        uid_str = str(uid)
        if uid_str not in self.active_writers:
            self.active_writers[uid_str] = set()
        self.active_writers[uid_str].add(writer)

    def unregister_writer(self, uid: str, writer):
        uid_str = str(uid)
        if uid_str in self.active_writers:
            self.active_writers[uid_str].discard(writer)
            if not self.active_writers[uid_str]:
                self.active_writers.pop(uid_str, None)

    def close_writers_for_account(self, uid: str):
        uid_str = str(uid)
        candidates = {uid_str}
        if uid_str in self.auth_to_game_id:
            candidates.add(str(self.auth_to_game_id[uid_str]))
        if uid_str in self.game_to_auth_id:
            candidates.add(str(self.game_to_auth_id[uid_str]))
        if uid_str in self.account_token_map:
            mapped = self.account_token_map[uid_str]
            candidates.add(str(mapped))
            candidates.add(str(mapped)[:16])

        for c in list(candidates):
            writers = list(self.active_writers.get(c, []))
            for w in writers:
                try:
                    if hasattr(w, "close"):
                        if hasattr(w, "is_closing"):
                            if not w.is_closing():
                                w.close()
                        else:
                            w.close()
                except Exception:
                    pass
            self.active_writers.pop(c, None)

    def log(self, message: str, level: str = "info", uid: Optional[str] = None):
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "level": level,
            "message": message,
            "uid": str(uid) if uid else None
        }
        self.logs.append(entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def register_account(self, uid: str, nickname: str, region: str, level: int, exp: int,
                         likes: int = 0, token: Optional[str] = None, auth_uid: Optional[str] = None):
        uid_str = str(uid)
        auth_uid_str = str(auth_uid) if auth_uid else self.game_to_auth_id.get(uid_str, "")
        if auth_uid_str:
            self.auth_to_game_id[auth_uid_str] = uid_str
            self.game_to_auth_id[uid_str] = auth_uid_str
            self.account_token_map[auth_uid_str] = uid_str
            self.account_token_map[uid_str] = auth_uid_str
        if token:
            self.account_token_map[uid_str] = token
            self.account_token_map[token[:16]] = uid_str
            if auth_uid_str:
                self.account_token_map[auth_uid_str] = token

        prog = calculate_level_progress(level or 1, exp)

        lvl_val = level or 1
        acc_mode = "BR" if lvl_val < 3 else "LONE_WOLF"
        acc_mode_label = "Battle Royale (Lvl < 3)" if lvl_val < 3 else "Lone Wolf (Lvl 3+)"

        if uid_str not in self.accounts:
            self.accounts[uid_str] = {
                "uid": uid_str,
                "auth_uid": auth_uid_str or "",
                "nickname": nickname or f"Player_{uid_str[:6]}",
                "region": region or "BD",
                "level": lvl_val,
                "next_level": prog["next_level"],
                "mode": acc_mode,
                "mode_label": acc_mode_label,
                "initial_exp": exp,
                "current_exp": exp,
                "gained_exp": 0,
                "remaining_exp": prog["remaining_exp"],
                "target_exp": prog["target_exp"],
                "needed_for_level": prog["needed_for_level"],
                "earned_in_level": prog["earned_in_level"],
                "progress_pct": prog["progress_pct"],
                "likes": likes or 0,
                "status": "PAUSED" if self.is_paused(uid_str) else "ONLINE",
                "matches_played": 0,
                "active_matches": 0,
                "last_match_time": None,
                "token": token or "",
                "start_time": time.time(),
                "is_paused": self.is_paused(uid_str),
                "paused_at": time.time() if self.is_paused(uid_str) else None,
                "total_pause_duration": 0.0,
                "last_updated": time.strftime("%H:%M:%S")
            }
        else:
            acc = self.accounts[uid_str]
            if auth_uid_str:
                acc["auth_uid"] = auth_uid_str
            if nickname:
                acc["nickname"] = nickname
            if region:
                acc["region"] = region
            if level:
                acc["level"] = level
            if token:
                acc["token"] = token
            acc["current_exp"] = exp
            acc["gained_exp"] = max(0, exp - acc["initial_exp"])
            acc["next_level"] = prog["next_level"]
            acc["remaining_exp"] = prog["remaining_exp"]
            acc["target_exp"] = prog["target_exp"]
            acc["needed_for_level"] = prog["needed_for_level"]
            acc["earned_in_level"] = prog["earned_in_level"]
            acc["progress_pct"] = prog["progress_pct"]
            acc["likes"] = likes
            if not acc.get("is_paused"):
                acc["status"] = "ONLINE"
            acc["last_updated"] = time.strftime("%H:%M:%S")
        self.recalc_totals()

    def get_account_uptime(self, uid_str: str) -> int:
        acc = self.accounts.get(uid_str)
        if not acc:
            mapped = self.game_to_auth_id.get(uid_str) or self.auth_to_game_id.get(uid_str)
            if mapped and mapped in self.accounts:
                acc = self.accounts[mapped]
        if not acc:
            return 0
        start_t = acc.get("start_time", time.time())
        total_pause = acc.get("total_pause_duration", 0.0)
        if acc.get("is_paused") and acc.get("paused_at"):
            return max(0, int(acc["paused_at"] - start_t - total_pause))
        return max(0, int(time.time() - start_t - total_pause))

    def is_paused(self, uid: str) -> bool:
        uid_str = str(uid)
        if uid_str in self.paused_accounts:
            return True
        game_id = self.auth_to_game_id.get(uid_str)
        if game_id and game_id in self.paused_accounts:
            return True
        auth_uid = self.game_to_auth_id.get(uid_str)
        if auth_uid and auth_uid in self.paused_accounts:
            return True
        acc = self.accounts.get(uid_str) or (self.accounts.get(game_id) if game_id else None)
        if acc and acc.get("is_paused"):
            return True
        return False

    def toggle_pause(self, uid: str) -> bool:
        uid_str = str(uid)
        candidates = {uid_str}
        if uid_str in self.auth_to_game_id:
            candidates.add(self.auth_to_game_id[uid_str])
        if uid_str in self.game_to_auth_id:
            candidates.add(self.game_to_auth_id[uid_str])

        target_acc = None
        target_key = uid_str
        for c in candidates:
            if c in self.accounts:
                target_acc = self.accounts[c]
                target_key = c
                break

        is_now_paused = not self.is_paused(uid_str)
        if is_now_paused:
            for c in candidates:
                self.paused_accounts.add(c)
                self.close_writers_for_account(c)
            if target_acc:
                target_acc["is_paused"] = True
                target_acc["paused_at"] = time.time()
                target_acc["status"] = "PAUSED"
            nick = target_acc.get("nickname", target_key) if target_acc else target_key
            self.log(f"⏸ UID {target_key} ({nick}) matchmaking PAUSED (TCP socket disconnected).", "warning", target_key)
            if "on_pause_toggle" in self.refresh_callbacks:
                try:
                    asyncio.create_task(self.refresh_callbacks["on_pause_toggle"](target_key, True))
                except Exception:
                    pass
        else:
            for c in candidates:
                self.paused_accounts.discard(c)
            if target_acc:
                target_acc["is_paused"] = False
                if target_acc.get("paused_at"):
                    pause_dur = time.time() - target_acc["paused_at"]
                    target_acc["total_pause_duration"] = target_acc.get("total_pause_duration", 0.0) + pause_dur
                    target_acc["paused_at"] = None
                target_acc["status"] = "ONLINE"
            nick = target_acc.get("nickname", target_key) if target_acc else target_key
            self.log(f"▶ UID {target_key} ({nick}) matchmaking RESUMED.", "success", target_key)
            if "on_pause_toggle" in self.refresh_callbacks:
                try:
                    asyncio.create_task(self.refresh_callbacks["on_pause_toggle"](target_key, False))
                except Exception:
                    pass

        return is_now_paused

    def toggle_pause_all(self) -> bool:
        any_active = any(not self.is_paused(k) for k in self.accounts.keys())
        for k in list(self.accounts.keys()):
            current_paused = self.is_paused(k)
            if any_active and not current_paused:
                self.toggle_pause(k)
            elif not any_active and current_paused:
                self.toggle_pause(k)
        return any_active

    def update_exp(self, uid: str, current_exp: int, level: Optional[int] = None):
        uid_str = str(uid)
        if uid_str in self.accounts:
            acc = self.accounts[uid_str]
            old_exp = acc["current_exp"]
            old_level = acc.get("level", 1)
            acc["current_exp"] = current_exp
            if level is not None and level > 0:
                acc["level"] = level
            acc["gained_exp"] = max(0, current_exp - acc["initial_exp"])
            
            current_lvl = acc["level"]
            acc["mode"] = "BR" if current_lvl < 3 else "LONE_WOLF"
            acc["mode_label"] = "Battle Royale (Lvl < 3)" if current_lvl < 3 else "Lone Wolf (Lvl 3+)"

            prog = calculate_level_progress(acc["level"], current_exp)
            acc["next_level"] = prog["next_level"]
            acc["remaining_exp"] = prog["remaining_exp"]
            acc["target_exp"] = prog["target_exp"]
            acc["needed_for_level"] = prog["needed_for_level"]
            acc["earned_in_level"] = prog["earned_in_level"]
            acc["progress_pct"] = prog["progress_pct"]
            acc["last_updated"] = time.strftime("%H:%M:%S")

            # Check for Level 2 -> 3 Mode Transition
            if old_level < 3 and current_lvl >= 3:
                self.log(
                    f"🎉 LEVEL UP! UID {uid_str} ({acc['nickname']}) reached Level {current_lvl}! Switching from Battle Royale to Lone Wolf mode!",
                    "success",
                    uid_str
                )

            diff = current_exp - old_exp
            if diff > 0:
                self.log(
                    f"★ UID {uid_str} ({acc['nickname']}) gained +{diff:,} EXP | Level {acc['level']} [{acc['mode']}] ({prog['progress_pct']}% - {prog['remaining_exp']:,} EXP to Lvl {prog['next_level']})",
                    "success",
                    uid_str
                )
            self.recalc_totals()

    def get_account_level(self, uid: str) -> int:
        uid_str = str(uid)
        acc = self.accounts.get(uid_str)
        if not acc:
            mapped = self.game_to_auth_id.get(uid_str) or self.auth_to_game_id.get(uid_str)
            if mapped and mapped in self.accounts:
                acc = self.accounts[mapped]
        if acc:
            return int(acc.get("level", 1) or 1)
        return 1

    def get_account_mode(self, uid: str) -> str:
        lvl = self.get_account_level(uid)
        return "BR" if lvl < 3 else "LONE_WOLF"

    def update_status(self, uid: str, status: str, active_matches: Optional[int] = None):
        uid_str = str(uid)
        if uid_str in self.accounts:
            self.accounts[uid_str]["status"] = status
            if active_matches is not None:
                self.accounts[uid_str]["active_matches"] = active_matches
            self.accounts[uid_str]["last_updated"] = time.strftime("%H:%M:%S")


    def increment_match_started(self):
        """Track total matches STARTED (not completed)"""
        self.total_matches_started += 1

    def increment_match(self, uid: str):
        uid_str = str(uid)
        self.total_matches += 1
        if uid_str in self.accounts:
            self.accounts[uid_str]["matches_played"] += 1
            self.accounts[uid_str]["last_match_time"] = time.strftime("%H:%M:%S")
            self.accounts[uid_str]["last_updated"] = time.strftime("%H:%M:%S")
            self.log(f"⚔ Match #{self.accounts[uid_str]['matches_played']} finished for {self.accounts[uid_str]['nickname']} ({uid_str})", "info", uid_str)

    def recalc_totals(self):
        self.total_gained_exp = sum(acc.get("gained_exp", 0) for acc in self.accounts.values())


bot_state = BotState()


# Fallback HTML if templates/index.html is missing
FALLBACK_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>DEVELOPER ZONE — Command Center</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">

<style>
:root{
    --void:#03040a;
    --void-2:#06080f;
    --panel:rgba(10,14,24,.72);
    --panel-solid:#0a0e18;
    --border:rgba(255,255,255,.055);
    --border-glow:rgba(0,240,255,.28);

    --neon-cyan:#00f0ff;
    --neon-blue:#4488ff;
    --neon-violet:#a855f7;
    --neon-pink:#ff2d95;
    --neon-lime:#7cff4a;
    --neon-amber:#ffb84d;
    --neon-red:#ff2d55;

    --text:#eef4ff;
    --text-dim:#6b7c99;
    --text-muted:#3d4a60;

    --shadow-sm:0 4px 20px rgba(0,0,0,.35);
    --shadow-md:0 12px 40px rgba(0,0,0,.5);
    --shadow-lg:0 25px 80px rgba(0,0,0,.65);
    --shadow-neon:0 0 40px rgba(0,240,255,.25);

    --r-sm:10px;
    --r-md:16px;
    --r-lg:22px;
    --r-xl:28px;
}

*{
    box-sizing:border-box;
    margin:0;
    padding:0;
    font-family:Inter,system-ui,sans-serif;
    -webkit-tap-highlight-color:transparent;
}

html,body{
    min-height:100vh;
    background:var(--void);
    color:var(--text);
    overflow-x:hidden;
}

/* ============================================
   AURORA BACKGROUND
============================================ */

body::before{
    content:"";
    position:fixed;
    inset:0;
    z-index:0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 0%, rgba(0,240,255,.15), transparent 50%),
        radial-gradient(ellipse 70% 50% at 80% 20%, rgba(168,85,247,.13), transparent 50%),
        radial-gradient(ellipse 90% 70% at 50% 100%, rgba(255,45,149,.10), transparent 50%),
        radial-gradient(ellipse 60% 40% at 10% 80%, rgba(68,136,255,.09), transparent 50%);
    pointer-events:none;
    animation:auroraShift 20s ease-in-out infinite alternate;
}

@keyframes auroraShift{
    0%{transform:scale(1) rotate(0deg)}
    100%{transform:scale(1.15) rotate(3deg)}
}

body::after{
    content:"";
    position:fixed;
    inset:0;
    z-index:0;
    pointer-events:none;
    opacity:.5;
    background-image:
        linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
    background-size:48px 48px;
    mask-image:radial-gradient(ellipse at center, black 30%, transparent 75%);
}

/* ============================================
   LOGIN
============================================ */

#login-screen{
    position:fixed;
    inset:0;
    z-index:9999;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:20px;
    background:rgba(2,4,9,.94);
    backdrop-filter:blur(30px) saturate(150%);
}

.login-card{
    position:relative;
    width:100%;
    max-width:440px;
    padding:44px 38px;
    border-radius:32px;
    background:linear-gradient(160deg, rgba(15,22,38,.85), rgba(5,8,16,.95));
    border:1px solid rgba(0,240,255,.14);
    box-shadow:
        0 0 0 1px rgba(255,255,255,.02),
        0 40px 120px rgba(0,0,0,.85),
        0 0 100px rgba(0,240,255,.10),
        inset 0 1px 0 rgba(255,255,255,.05);
    animation:loginRise .7s cubic-bezier(.2,.9,.2,1);
    overflow:hidden;
}

.login-card::before{
    content:"";
    position:absolute;
    top:-2px; left:20%; right:20%;
    height:2px;
    background:linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-violet), transparent);
    filter:blur(1px);
    animation:scanLine 3s ease-in-out infinite;
}

@keyframes scanLine{
    0%,100%{opacity:.4; transform:scaleX(.6)}
    50%{opacity:1; transform:scaleX(1.2)}
}

@keyframes loginRise{
    from{opacity:0; transform:translateY(40px) scale(.92); filter:blur(10px)}
    to{opacity:1; transform:none; filter:none}
}

.logo-wrap{
    position:relative;
    width:92px;
    height:92px;
    margin:0 auto 26px;
}

.logo-ring{
    position:absolute;
    inset:0;
    border-radius:26px;
    background:conic-gradient(from 0deg, var(--neon-cyan), var(--neon-violet), var(--neon-pink), var(--neon-cyan));
    animation:ringSpin 4s linear infinite;
    filter:blur(1px);
}

@keyframes ringSpin{to{transform:rotate(360deg)}}

.logo-core{
    position:absolute;
    inset:3px;
    border-radius:23px;
    background:linear-gradient(145deg,#0b1525,#050810);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:36px;
    color:var(--neon-cyan);
    text-shadow:0 0 30px var(--neon-cyan);
    z-index:1;
}

.brand-name{
    text-align:center;
    font-family:'Orbitron',sans-serif;
    font-size:28px;
    font-weight:900;
    letter-spacing:4px;
    background:linear-gradient(90deg, var(--neon-cyan), #fff, var(--neon-violet));
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:8px;
}

.brand-sub{
    text-align:center;
    color:var(--text-dim);
    font-size:11px;
    letter-spacing:3px;
    text-transform:uppercase;
    font-weight:600;
    margin-bottom:8px;
}

.brand-badge{
    display:flex;
    justify-content:center;
    margin-bottom:32px;
}

.brand-badge span{
    display:inline-flex;
    align-items:center;
    gap:7px;
    padding:6px 14px;
    border-radius:100px;
    background:rgba(0,240,255,.06);
    border:1px solid rgba(0,240,255,.22);
    color:var(--neon-cyan);
    font-size:10px;
    font-weight:800;
    letter-spacing:1.5px;
    text-transform:uppercase;
}

.brand-badge .dot{
    width:6px; height:6px;
    border-radius:50%;
    background:var(--neon-cyan);
    box-shadow:0 0 12px var(--neon-cyan);
    animation:dotPulse 1.5s infinite;
}

@keyframes dotPulse{
    0%,100%{opacity:1; transform:scale(1)}
    50%{opacity:.4; transform:scale(.6)}
}

.field-wrap{
    position:relative;
    margin-bottom:14px;
}

.field-wrap i.field-icon{
    position:absolute;
    left:20px;
    top:50%;
    transform:translateY(-50%);
    color:var(--text-muted);
    font-size:14px;
    transition:.25s;
}

.key-input{
    width:100%;
    padding:18px 52px 18px 50px;
    border-radius:14px;
    border:1px solid var(--border);
    background:rgba(255,255,255,.025);
    color:#fff;
    font-family:'JetBrains Mono',monospace;
    font-size:14px;
    letter-spacing:2px;
    outline:none;
    transition:.3s;
}

.key-input:focus{
    border-color:var(--neon-cyan);
    background:rgba(0,240,255,.04);
    box-shadow:
        0 0 0 3px rgba(0,240,255,.08),
        0 0 30px rgba(0,240,255,.15);
}

.key-input:focus ~ i.field-icon{
    color:var(--neon-cyan);
}

.key-eye{
    position:absolute;
    right:18px;
    top:50%;
    transform:translateY(-50%);
    background:none;
    border:0;
    color:var(--text-muted);
    cursor:pointer;
    padding:6px;
    transition:.25s;
}

.key-eye:hover{
    color:var(--neon-cyan);
}

.login-btn{
    position:relative;
    width:100%;
    margin-top:8px;
    padding:17px;
    border:0;
    border-radius:14px;
    cursor:pointer;
    font-family:Inter,sans-serif;
    font-size:13px;
    font-weight:900;
    letter-spacing:3px;
    text-transform:uppercase;
    color:#001018;
    background:linear-gradient(100deg, var(--neon-cyan), #7df9ff 30%, var(--neon-blue) 70%, var(--neon-violet));
    background-size:200% 100%;
    box-shadow:
        0 12px 40px rgba(0,240,255,.28),
        inset 0 1px 0 rgba(255,255,255,.5);
    transition:.3s;
    overflow:hidden;
}

.login-btn:hover{
    transform:translateY(-2px);
    background-position:100% 0;
    box-shadow:0 18px 60px rgba(0,240,255,.45);
}

.login-btn::before{
    content:"";
    position:absolute;
    top:0; left:-100%;
    width:100%; height:100%;
    background:linear-gradient(90deg, transparent, rgba(255,255,255,.4), transparent);
    transition:.6s;
}

.login-btn:hover::before{
    left:100%;
}

.login-err{
    min-height:16px;
    text-align:center;
    margin-top:8px;
    color:var(--neon-red);
    font-size:11px;
    font-weight:700;
    letter-spacing:1px;
}

.login-foot{
    margin-top:28px;
    padding-top:22px;
    border-top:1px solid var(--border);
    text-align:center;
    color:var(--text-muted);
    font-size:10px;
    letter-spacing:2px;
    text-transform:uppercase;
    font-weight:600;
    line-height:1.8;
}

.login-foot strong{
    color:var(--neon-cyan);
    font-weight:800;
}

/* ============================================
   MAIN APP
============================================ */

#app{
    display:none;
    position:relative;
    z-index:1;
}

.shell{
    max-width:1600px;
    margin:0 auto;
    padding:24px;
}

/* ---------- TOPBAR ---------- */

.topbar{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:20px;
    padding:20px 26px;
    border-radius:var(--r-lg);
    background:linear-gradient(135deg, rgba(10,15,26,.82), rgba(5,8,16,.88));
    border:1px solid var(--border);
    backdrop-filter:blur(24px);
    box-shadow:var(--shadow-md);
    position:relative;
    overflow:hidden;
}

.topbar::before{
    content:"";
    position:absolute;
    top:0; left:0; right:0;
    height:1px;
    background:linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
    opacity:.5;
}

.brand-block{
    display:flex;
    align-items:center;
    gap:16px;
}

.brand-mark{
    position:relative;
    width:56px;
    height:56px;
}

.brand-mark-core{
    position:absolute;
    inset:0;
    border-radius:18px;
    background:linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:26px;
    color:#001018;
    box-shadow:0 0 40px rgba(0,240,255,.4);
}

.brand-name-main{
    font-family:'Orbitron',sans-serif;
    font-size:22px;
    font-weight:900;
    letter-spacing:3px;
    background:linear-gradient(90deg, #fff, var(--neon-cyan));
    -webkit-background-clip:text;
    background-clip:text;
    -webkit-text-fill-color:transparent;
}

.brand-tag{
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:6px;
    color:var(--text-dim);
    font-size:10px;
    letter-spacing:2px;
    text-transform:uppercase;
    font-weight:700;
}

.live-pill{
    display:inline-flex;
    align-items:center;
    gap:6px;
    color:var(--neon-lime);
}

.live-pill .dot{
    width:6px;
    height:6px;
    border-radius:50%;
    background:var(--neon-lime);
    box-shadow:0 0 12px var(--neon-lime);
    animation:dotPulse 1.4s infinite;
}

.top-actions{
    display:flex;
    gap:10px;
}

.btn{
    padding:11px 18px;
    border-radius:12px;
    border:1px solid var(--border);
    background:rgba(255,255,255,.03);
    color:var(--text);
    font-family:Inter,sans-serif;
    font-size:12px;
    font-weight:800;
    letter-spacing:1px;
    cursor:pointer;
    transition:.25s;
    display:inline-flex;
    align-items:center;
    gap:8px;
}

.btn:hover{
    border-color:var(--border-glow);
    background:rgba(0,240,255,.06);
    transform:translateY(-2px);
    box-shadow:0 8px 24px rgba(0,240,255,.15);
}

.btn-primary{
    border:0;
    color:#001018;
    background:linear-gradient(100deg, var(--neon-cyan), var(--neon-blue));
    box-shadow:0 8px 28px rgba(0,240,255,.28);
}

.btn-primary:hover{
    box-shadow:0 12px 40px rgba(0,240,255,.5);
    color:#001018;
}

/* ---------- STATS GRID ---------- */

.stats{
    display:grid;
    grid-template-columns:repeat(5, 1fr);
    gap:16px;
    margin-top:20px;
}

.stat-card{
    position:relative;
    overflow:hidden;
    padding:22px;
    border-radius:var(--r-lg);
    background:linear-gradient(150deg, rgba(12,18,32,.7), rgba(6,9,18,.8));
    border:1px solid var(--border);
    backdrop-filter:blur(16px);
    transition:.3s;
}

.stat-card:hover{
    transform:translateY(-4px);
    border-color:var(--border-glow);
    box-shadow:0 20px 50px rgba(0,0,0,.4), 0 0 40px rgba(0,240,255,.08);
}

.stat-card::before{
    content:"";
    position:absolute;
    top:0; right:0;
    width:140px; height:140px;
    border-radius:50%;
    background:var(--neon-cyan);
    filter:blur(70px);
    opacity:.06;
    pointer-events:none;
}

.stat-card.violet::before{background:var(--neon-violet)}
.stat-card.lime::before{background:var(--neon-lime)}
.stat-card.pink::before{background:var(--neon-pink)}
.stat-card.amber::before{background:var(--neon-amber)}

.stat-ic{
    width:44px;
    height:44px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:17px;
    color:var(--neon-cyan);
    background:rgba(0,240,255,.08);
    border:1px solid rgba(0,240,255,.14);
    margin-bottom:16px;
}

.stat-card.violet .stat-ic{color:var(--neon-violet); background:rgba(168,85,247,.08); border-color:rgba(168,85,247,.18)}
.stat-card.lime .stat-ic{color:var(--neon-lime); background:rgba(124,255,74,.08); border-color:rgba(124,255,74,.18)}
.stat-card.pink .stat-ic{color:var(--neon-pink); background:rgba(255,45,149,.08); border-color:rgba(255,45,149,.18)}
.stat-card.amber .stat-ic{color:var(--neon-amber); background:rgba(255,184,77,.08); border-color:rgba(255,184,77,.18)}

.stat-label{
    display:block;
    color:var(--text-muted);
    font-size:9px;
    font-weight:800;
    letter-spacing:2px;
    text-transform:uppercase;
    margin-bottom:8px;
}

.stat-value{
    font-family:'Orbitron',sans-serif;
    font-size:28px;
    font-weight:900;
    letter-spacing:1px;
    color:var(--text);
    line-height:1;
    margin-bottom:8px;
}

.stat-card.violet .stat-value{color:var(--neon-violet)}
.stat-card.lime .stat-value{color:var(--neon-lime)}
.stat-card.pink .stat-value{color:var(--neon-pink)}
.stat-card.amber .stat-value{color:var(--neon-amber)}

.stat-foot{
    color:var(--text-muted);
    font-size:10px;
    letter-spacing:1px;
    font-weight:600;
}

/* ---------- WORKSPACE ---------- */

.workspace{
    display:grid;
    grid-template-columns:minmax(0,1fr) 460px;
    gap:20px;
    margin-top:20px;
}

.panel{
    background:linear-gradient(150deg, rgba(10,15,26,.78), rgba(5,8,16,.85));
    border:1px solid var(--border);
    border-radius:var(--r-lg);
    backdrop-filter:blur(20px);
    overflow:hidden;
    box-shadow:var(--shadow-md);
}

.panel-head{
    padding:20px 24px;
    border-bottom:1px solid var(--border);
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:14px;
}

.panel-title{
    display:flex;
    align-items:center;
    gap:12px;
}

.panel-ic{
    width:40px;
    height:40px;
    border-radius:12px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:var(--neon-cyan);
    background:rgba(0,240,255,.08);
    border:1px solid rgba(0,240,255,.14);
    font-size:15px;
}

.panel-title h3{
    font-size:15px;
    font-weight:800;
    letter-spacing:.5px;
    display:flex;
    align-items:center;
    gap:10px;
}

.chip{
    padding:4px 10px;
    border-radius:100px;
    font-size:10px;
    font-weight:800;
    font-family:'JetBrains Mono',monospace;
    color:var(--neon-cyan);
    background:rgba(0,240,255,.08);
    border:1px solid rgba(0,240,255,.16);
    letter-spacing:1px;
}

/* ---------- CONTROLS ---------- */

.controls{
    padding:16px 20px;
    display:flex;
    gap:12px;
    border-bottom:1px solid var(--border);
}

.search{
    flex:1;
    position:relative;
}

.search i{
    position:absolute;
    left:16px;
    top:50%;
    transform:translateY(-50%);
    color:var(--text-muted);
    font-size:13px;
}

.search input{
    width:100%;
    padding:12px 16px 12px 42px;
    border-radius:12px;
    border:1px solid var(--border);
    background:rgba(255,255,255,.025);
    color:#fff;
    font-size:12px;
    outline:none;
    transition:.25s;
}

.search input:focus{
    border-color:var(--border-glow);
    background:rgba(0,240,255,.03);
    box-shadow:0 0 20px rgba(0,240,255,.08);
}

.filters{
    display:flex;
    gap:4px;
    padding:4px;
    border-radius:12px;
    background:rgba(0,0,0,.35);
    border:1px solid var(--border);
}

.filter{
    border:0;
    background:transparent;
    color:var(--text-dim);
    padding:8px 13px;
    border-radius:8px;
    cursor:pointer;
    font-size:10px;
    font-weight:800;
    letter-spacing:1.2px;
    transition:.25s;
}

.filter.active{
    color:var(--neon-cyan);
    background:rgba(0,240,255,.1);
    box-shadow:0 0 15px rgba(0,240,255,.15);
}

/* ---------- ACCOUNT CARDS ---------- */

.accounts-wrap{
    max-height:720px;
    overflow-y:auto;
    padding:18px;
}

.accounts-wrap::-webkit-scrollbar,
.console-body::-webkit-scrollbar{
    width:6px;
}

.accounts-wrap::-webkit-scrollbar-thumb,
.console-body::-webkit-scrollbar-thumb{
    background:rgba(0,240,255,.2);
    border-radius:10px;
}

.account-card{
    position:relative;
    padding:20px;
    margin-bottom:14px;
    border-radius:var(--r-md);
    background:linear-gradient(140deg, rgba(14,20,36,.7), rgba(6,9,16,.7));
    border:1px solid var(--border);
    transition:.3s;
    overflow:hidden;
}

.account-card::before{
    content:"";
    position:absolute;
    left:0; top:0; bottom:0;
    width:3px;
    background:linear-gradient(to bottom, var(--neon-cyan), var(--neon-violet));
    opacity:.7;
}

.account-card:hover{
    transform:translateY(-3px);
    border-color:var(--border-glow);
    box-shadow:0 16px 45px rgba(0,0,0,.4), 0 0 30px rgba(0,240,255,.07);
}

.acc-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:16px;
}

.acc-id{
    display:flex;
    align-items:center;
    gap:14px;
    min-width:0;
}

.acc-avatar{
    position:relative;
    width:52px; height:52px;
    flex-shrink:0;
}

.acc-avatar-ring{
    position:absolute;
    inset:0;
    border-radius:15px;
    background:conic-gradient(from 0deg, var(--neon-cyan), var(--neon-violet), var(--neon-pink), var(--neon-cyan));
    animation:ringSpin 6s linear infinite;
    opacity:.85;
}

.acc-avatar-core{
    position:absolute;
    inset:2px;
    border-radius:13px;
    background:linear-gradient(145deg, #0d1524, #050810);
    display:flex;
    align-items:center;
    justify-content:center;
    color:var(--neon-cyan);
    font-size:19px;
}

.acc-level{
    position:absolute;
    right:-6px;
    bottom:-6px;
    padding:3px 7px;
    border-radius:7px;
    font-size:9px;
    font-weight:900;
    font-family:'JetBrains Mono',monospace;
    color:#001018;
    background:linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
    box-shadow:0 0 15px rgba(0,240,255,.6);
    border:2px solid #03060e;
}

.acc-name{
    font-size:14px;
    font-weight:800;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
    letter-spacing:.3px;
    display:flex;
    align-items:center;
    gap:8px;
}

.acc-region{
    padding:2px 7px;
    border-radius:6px;
    font-size:9px;
    font-weight:900;
    letter-spacing:1px;
    color:var(--neon-violet);
    background:rgba(168,85,247,.1);
    border:1px solid rgba(168,85,247,.22);
}

.acc-uid{
    display:flex;
    align-items:center;
    gap:8px;
    margin-top:6px;
    color:var(--text-dim);
    font-family:'JetBrains Mono',monospace;
    font-size:10px;
    letter-spacing:1px;
}

.copy-btn{
    border:0;
    background:none;
    color:var(--text-muted);
    cursor:pointer;
    padding:2px;
    transition:.2s;
}

.copy-btn:hover{
    color:var(--neon-cyan);
}

.acc-uptime{
    color:var(--neon-cyan);
    font-family:'JetBrains Mono',monospace;
    font-size:10px;
    display:inline-flex;
    align-items:center;
    gap:4px;
}

.status-pill{
    display:inline-flex;
    align-items:center;
    gap:7px;
    padding:6px 12px;
    border-radius:100px;
    font-size:9px;
    font-weight:900;
    letter-spacing:1.2px;
    border:1px solid;
    text-transform:uppercase;
    flex-shrink:0;
}

.status-pill .sdot{
    width:6px; height:6px;
    border-radius:50%;
    background:currentColor;
    box-shadow:0 0 10px currentColor;
    animation:dotPulse 1.6s infinite;
}

.status-online{
    color:var(--neon-lime);
    background:rgba(124,255,74,.06);
    border-color:rgba(124,255,74,.24);
}

.status-match{
    color:var(--neon-cyan);
    background:rgba(0,240,255,.07);
    border-color:rgba(0,240,255,.3);
    box-shadow:0 0 20px rgba(0,240,255,.2);
}

.status-search{
    color:var(--neon-amber);
    background:rgba(255,184,77,.06);
    border-color:rgba(255,184,77,.24);
}

.status-paused{
    color:var(--neon-amber);
    background:rgba(255,184,77,.06);
    border-color:rgba(255,184,77,.24);
}

.status-error{
    color:var(--neon-red);
    background:rgba(255,45,85,.06);
    border-color:rgba(255,45,85,.24);
}

/* ---------- METRICS ---------- */

.acc-metrics{
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:10px;
    margin-bottom:14px;
}

.metric-box{
    padding:12px;
    border-radius:12px;
    background:rgba(0,0,0,.28);
    border:1px solid rgba(255,255,255,.04);
    transition:.25s;
}

.metric-box:hover{
    background:rgba(0,0,0,.4);
    border-color:rgba(0,240,255,.14);
}

.metric-box span{
    display:block;
    color:var(--text-muted);
    font-size:8px;
    font-weight:800;
    letter-spacing:1.5px;
    text-transform:uppercase;
    margin-bottom:6px;
}

.metric-box strong{
    display:block;
    font-family:'JetBrains Mono',monospace;
    font-size:14px;
    font-weight:700;
    letter-spacing:.5px;
    color:var(--text);
}

.metric-box.gain strong{
    color:var(--neon-lime);
    text-shadow:0 0 15px rgba(124,255,74,.4);
}

/* ---------- PROGRESS ---------- */

.progress-block{
    padding:14px;
    border-radius:12px;
    background:rgba(0,0,0,.25);
    border:1px solid rgba(255,255,255,.04);
    margin-bottom:14px;
}

.progress-top{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:10px;
    margin-bottom:10px;
    font-size:10px;
    color:var(--text-dim);
    letter-spacing:.5px;
}

.progress-top b{
    color:var(--neon-cyan);
    font-family:'JetBrains Mono',monospace;
    font-weight:700;
}

.progress-track{
    height:9px;
    border-radius:100px;
    background:rgba(0,0,0,.5);
    border:1px solid rgba(255,255,255,.04);
    overflow:hidden;
    position:relative;
}

.progress-fill{
    height:100%;
    border-radius:100px;
    background:linear-gradient(90deg, var(--neon-blue), var(--neon-cyan), var(--neon-lime));
    background-size:200% 100%;
    animation:gradFlow 2s linear infinite;
    box-shadow:0 0 20px rgba(0,240,255,.45);
    transition:width .8s cubic-bezier(.2,.9,.2,1);
    position:relative;
}

.progress-fill::after{
    content:"";
    position:absolute;
    right:0; top:0; bottom:0;
    width:20px;
    background:linear-gradient(90deg, transparent, rgba(255,255,255,.5));
    filter:blur(3px);
}

@keyframes gradFlow{to{background-position:200% 0}}

.progress-bot{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-top:8px;
    color:var(--text-muted);
    font-size:9px;
    font-family:'JetBrains Mono',monospace;
}

.progress-bot .pct{
    color:var(--neon-cyan);
    font-weight:800;
    font-size:11px;
}

/* ---------- CARD FOOTER ---------- */

.acc-foot{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    padding-top:14px;
    border-top:1px solid rgba(255,255,255,.04);
}

.acc-time{
    color:var(--text-muted);
    font-size:10px;
    display:inline-flex;
    align-items:center;
    gap:6px;
}

.acc-actions{
    display:flex;
    gap:7px;
}

.act-btn{
    width:36px;
    height:36px;
    border-radius:11px;
    border:1px solid var(--border);
    background:rgba(255,255,255,.03);
    color:var(--text-dim);
    cursor:pointer;
    font-size:13px;
    transition:.25s;
    display:flex;
    align-items:center;
    justify-content:center;
}

.act-btn:hover{
    color:var(--neon-cyan);
    border-color:var(--border-glow);
    background:rgba(0,240,255,.06);
    transform:translateY(-2px);
}

.act-btn.danger:hover{
    color:var(--neon-red);
    border-color:rgba(255,45,85,.3);
    background:rgba(255,45,85,.06);
}

/* ---------- CONSOLE ---------- */

.console-panel{
    display:flex;
    flex-direction:column;
    min-height:850px;
}

.console-tools{
    padding:14px 18px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:10px;
    border-bottom:1px solid var(--border);
}

.console-filters{
    display:flex;
    gap:5px;
    flex-wrap:wrap;
}

.cfilter{
    padding:6px 11px;
    border-radius:8px;
    border:1px solid var(--border);
    background:transparent;
    color:var(--text-muted);
    cursor:pointer;
    font-size:9px;
    font-weight:800;
    letter-spacing:1px;
    transition:.25s;
}

.cfilter:hover{
    color:var(--text);
    border-color:var(--border-glow);
}

.cfilter.active{
    color:var(--neon-cyan);
    background:rgba(0,240,255,.08);
    border-color:rgba(0,240,255,.28);
}

.console-body{
    flex:1;
    margin:16px;
    padding:16px;
    border-radius:14px;
    background:#02040a;
    border:1px solid rgba(0,240,255,.08);
    overflow-y:auto;
    font:10.5px/1.75 'JetBrains Mono',monospace;
    position:relative;
}

.console-body::before{
    content:"";
    position:absolute;
    inset:0;
    pointer-events:none;
    background:repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,240,255,.012) 2px,
        rgba(0,240,255,.012) 4px
    );
}

.log-line{
    display:flex;
    gap:10px;
    margin-bottom:6px;
    word-break:break-word;
    position:relative;
    z-index:1;
}

.log-ts{
    color:#2f3d52;
    flex-shrink:0;
    font-weight:500;
}

.log-msg{color:#9cb3d0}
.log-msg.success{color:var(--neon-lime); text-shadow:0 0 10px rgba(124,255,74,.25)}
.log-msg.warning{color:var(--neon-amber); text-shadow:0 0 10px rgba(255,184,77,.25)}
.log-msg.error{color:var(--neon-red); text-shadow:0 0 10px rgba(255,45,85,.3)}
.log-msg.info{color:#7dcfff}

.console-foot{
    padding:12px 18px;
    border-top:1px solid var(--border);
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:var(--text-muted);
    font-size:9px;
    letter-spacing:1.5px;
    text-transform:uppercase;
    font-weight:700;
}

.console-foot .live-tag{
    display:inline-flex;
    align-items:center;
    gap:6px;
    color:var(--neon-lime);
}

/* ---------- EMPTY ---------- */

.empty-state{
    text-align:center;
    padding:80px 24px;
    color:var(--text-muted);
}

.empty-state i{
    font-size:44px;
    color:#1a2739;
    margin-bottom:20px;
    display:block;
}

.empty-state p{
    font-size:12px;
    margin-bottom:20px;
    letter-spacing:1px;
}

/* ---------- MODAL ---------- */

.modal-bg{
    position:fixed;
    inset:0;
    z-index:5000;
    display:none;
    align-items:center;
    justify-content:center;
    padding:20px;
    background:rgba(2,4,9,.82);
    backdrop-filter:blur(20px);
}

.modal-bg.active{
    display:flex;
}

.modal-card{
    width:100%;
    max-width:520px;
    padding:32px;
    border-radius:26px;
    background:linear-gradient(160deg, #0d1524, #050810);
    border:1px solid rgba(0,240,255,.18);
    box-shadow:0 40px 120px rgba(0,0,0,.85), 0 0 80px rgba(0,240,255,.1);
    animation:modalRise .3s cubic-bezier(.2,.9,.2,1);
}

@keyframes modalRise{
    from{opacity:0; transform:translateY(30px) scale(.94)}
    to{opacity:1; transform:none}
}

.modal-head{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:24px;
}

.modal-head h3{
    font-family:'Orbitron',sans-serif;
    font-size:17px;
    font-weight:900;
    letter-spacing:1.5px;
    display:flex;
    align-items:center;
    gap:10px;
}

.modal-head h3 i{color:var(--neon-cyan)}

.modal-close{
    width:36px; height:36px;
    border-radius:10px;
    border:1px solid var(--border);
    background:rgba(255,255,255,.03);
    color:var(--text-dim);
    cursor:pointer;
    transition:.25s;
}

.modal-close:hover{
    color:var(--neon-red);
    border-color:rgba(255,45,85,.3);
}

.field-block{
    margin-bottom:18px;
}

.field-block label{
    display:block;
    margin-bottom:8px;
    color:var(--text-dim);
    font-size:10px;
    font-weight:800;
    letter-spacing:1.5px;
    text-transform:uppercase;
}

.field-input,
.field-select,
.field-textarea{
    width:100%;
    padding:14px 16px;
    border-radius:12px;
    border:1px solid var(--border);
    background:rgba(255,255,255,.025);
    color:#fff;
    font-family:'JetBrains Mono',monospace;
    font-size:13px;
    outline:none;
    transition:.25s;
}

.field-input:focus,
.field-select:focus,
.field-textarea:focus{
    border-color:var(--border-glow);
    background:rgba(0,240,255,.03);
    box-shadow:0 0 20px rgba(0,240,255,.12);
}

.field-select{
    cursor:pointer;
    font-family:Inter,sans-serif;
    appearance:none;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7c99' stroke-width='2'><polyline points='6 9 12 15 18 9'/></svg>");
    background-repeat:no-repeat;
    background-position:right 16px center;
    padding-right:42px;
}

.field-select option{
    background:#0a0e18;
    color:#fff;
}

.field-textarea{
    resize:vertical;
    min-height:100px;
}

.modal-actions{
    display:flex;
    justify-content:flex-end;
    gap:10px;
    margin-top:24px;
}

/* ---------- TOAST ---------- */

.toast-wrap{
    position:fixed;
    top:20px;
    right:20px;
    z-index:10000;
    display:flex;
    flex-direction:column;
    gap:10px;
    pointer-events:none;
}

.toast{
    display:flex;
    align-items:center;
    gap:12px;
    min-width:260px;
    max-width:400px;
    padding:14px 18px;
    border-radius:14px;
    background:rgba(8,13,23,.95);
    border:1px solid var(--border);
    backdrop-filter:blur(20px);
    box-shadow:0 20px 50px rgba(0,0,0,.6);
    color:#fff;
    font-size:12px;
    font-weight:700;
    letter-spacing:.3px;
    animation:toastIn .35s cubic-bezier(.2,.9,.2,1);
    pointer-events:auto;
}

.toast i{
    font-size:15px;
}

.toast.success{
    border-color:rgba(124,255,74,.28);
    box-shadow:0 20px 50px rgba(0,0,0,.6), 0 0 30px rgba(124,255,74,.1);
}

.toast.success i{color:var(--neon-lime)}

.toast.error{
    border-color:rgba(255,45,85,.28);
    box-shadow:0 20px 50px rgba(0,0,0,.6), 0 0 30px rgba(255,45,85,.1);
}

.toast.error i{color:var(--neon-red)}

.toast.info{
    border-color:rgba(0,240,255,.28);
}

.toast.info i{color:var(--neon-cyan)}

@keyframes toastIn{
    from{opacity:0; transform:translateX(40px)}
    to{opacity:1; transform:none}
}

/* ---------- MOBILE NAV ---------- */

.mobile-nav{display:none}

/* ---------- RESPONSIVE ---------- */

@media(max-width:1350px){
    .stats{grid-template-columns:repeat(3,1fr)}
}

@media(max-width:1100px){
    .workspace{grid-template-columns:1fr}
    .console-panel{min-height:600px}
}

@media(max-width:800px){
    .shell{padding:14px; padding-bottom:90px}

    .stats{grid-template-columns:1fr 1fr; gap:10px}
    .stat-card{padding:16px}
    .stat-value{font-size:20px}
    .stat-ic{width:38px;height:38px;font-size:15px;margin-bottom:12px}

    .topbar{padding:14px 16px; border-radius:18px}
    .brand-mark{width:46px;height:46px}
    .brand-mark-core{font-size:22px}
    .brand-name-main{font-size:16px; letter-spacing:2px}
    .brand-tag{font-size:8px; gap:6px}
    .brand-tag .hide-sm{display:none}

    .top-actions .btn{padding:9px 12px}
    .top-actions .btn .hide-sm{display:none}

    .controls{flex-direction:column}
    .filters{overflow-x:auto}
    .filter{flex:1; white-space:nowrap}

    .accounts-wrap{padding:12px; max-height:none}

    .account-card{padding:16px}
    .acc-avatar{width:46px; height:46px}
    .acc-metrics{gap:8px}
    .metric-box{padding:10px}
    .metric-box strong{font-size:12px}

    .workspace{margin-top:12px}
    .panel-head{padding:16px}
    .panel-title h3{font-size:13px}
    .console-panel{min-height:calc(100vh - 180px)}

    .mobile-nav{
        position:fixed;
        bottom:0; left:0; right:0;
        height:70px;
        z-index:4000;
        display:flex;
        align-items:center;
        justify-content:space-around;
        padding:6px;
        background:rgba(4,7,14,.94);
        border-top:1px solid var(--border);
        backdrop-filter:blur(24px);
    }

    .nav-btn{
        flex:1;
        border:0;
        background:none;
        color:var(--text-muted);
        display:flex;
        flex-direction:column;
        align-items:center;
        gap:5px;
        font-size:9px;
        font-weight:800;
        letter-spacing:1px;
        padding:8px 6px;
        border-radius:12px;
        cursor:pointer;
        transition:.25s;
    }

    .nav-btn i{font-size:18px}

    .nav-btn.active{
        color:var(--neon-cyan);
        background:rgba(0,240,255,.07);
    }

    .mobile-tab{display:none}
    .mobile-tab.active{display:block}
    .console-panel.mobile-tab.active{display:flex}

    .modal-bg{align-items:flex-end; padding:0}
    .modal-card{border-radius:24px 24px 0 0; padding:26px 20px 34px}

    .toast-wrap{left:12px; right:12px; top:12px}
    .toast{max-width:none; min-width:0}
}

@media(max-width:420px){
    .login-card{padding:30px 22px}
    .brand-name{font-size:22px; letter-spacing:2px}
    .acc-metrics{grid-template-columns:1fr 1fr}
    .acc-metrics .metric-box:nth-child(3){grid-column:span 2}
}

/* Admin Panel Styles */
.admin-section{
    padding:16px;
    border-radius:12px;
    background:rgba(0,0,0,.25);
    border:1px solid rgba(255,255,255,.04);
}

.admin-section h4{
    color:var(--neon-cyan);
    font-size:12px;
    font-weight:700;
    margin-bottom:12px;
    text-transform:uppercase;
    letter-spacing:1px;
}

.key-item{
    transition:.2s;
}

.key-item:hover{
    background:rgba(0,240,255,.05);
}
</style>
</head>

<body>

<!-- ============================================
     LOGIN SCREEN
============================================ -->

<section id="login-screen">
    <div class="login-card">
        <div class="logo-wrap">
            <div class="logo-ring"></div>
            <div class="logo-core">
                <i class="fa-solid fa-bolt"></i>
            </div>
        </div>

        <div class="brand-name">TOXIC LEVEL UP</div>
        <div class="brand-sub">Command Center</div>

        <div class="brand-badge">
            <span><span class="dot"></span>Developer Zone</span>
        </div>

        <form onsubmit="login(event)">
            <div class="field-wrap">
                <i class="fa-solid fa-key field-icon"></i>
                <input
                    id="login-key"
                    class="key-input"
                    type="password"
                    placeholder="ENTER ACCESS KEY"
                    autocomplete="off"
                >
                <button type="button" class="key-eye" onclick="toggleKey()">
                    <i id="key-eye" class="fa-solid fa-eye"></i>
                </button>
            </div>

            <div id="login-error" class="login-err"></div>

            <button class="login-btn" type="submit">
                <i class="fa-solid fa-shield-halved"></i> Unlock Command Center
            </button>
        </form>

        <div class="login-foot">
            Protected Access • <strong>Premium Engine</strong><br>
            TOXIC LEVEL UP • Level Up System
        </div>
    </div>
</section>

<!-- ============================================
     MAIN APP
============================================ -->

<div id="app">

<div class="toast-wrap" id="toast-wrap"></div>

<div class="shell">

    <!-- TOPBAR -->

    <header class="topbar">
        <div class="brand-block">
            <div class="brand-mark">
                <div class="brand-mark-core">
                    <i class="fa-solid fa-bolt"></i>
                </div>
            </div>
            <div>
                <div class="brand-name-main">TOXIC LEVEL UP</div>
                <div class="brand-tag">
                    <span class="live-pill">
                        <span class="dot"></span>ONLINE
                    </span>
                    <span class="hide-sm">•</span>
                    <span class="hide-sm">Developer Zone</span>
                    <span class="hide-sm">•</span>
                    <span class="hide-sm">Level Engine</span>
                </div>
            </div>
        </div>

        <div class="top-actions">
            <button class="btn" onclick="manualRefresh()">
                <i class="fa-solid fa-rotate"></i>
                <span class="hide-sm">Refresh</span>
            </button>
            <button class="btn" id="admin-btn" onclick="openAdminPanel()" style="display:none;">
                <i class="fa-solid fa-user-shield"></i>
                <span class="hide-sm">Admin Panel</span>
            </button>
            <button class="btn btn-primary" onclick="openAddModal()">
                <i class="fa-solid fa-plus"></i>
                <span class="hide-sm">Add Account</span>
            </button>
            <button class="btn" onclick="logout()">
                <i class="fa-solid fa-right-from-bracket"></i>
                <span class="hide-sm">Logout</span>
            </button>
        </div>
    </header>

    <!-- STATS -->

    <section class="stats">
        <div class="stat-card">
            <div class="stat-ic"><i class="fa-solid fa-users"></i></div>
            <span class="stat-label">Active Accounts</span>
            <div class="stat-value" id="stat-accounts">0</div>
            <div class="stat-foot" id="stat-online">0 Online</div>
        </div>

        <div class="stat-card violet">
            <div class="stat-ic"><i class="fa-solid fa-rocket"></i></div>
            <span class="stat-label">Matches Started</span>
            <div class="stat-value" id="stat-started">0</div>
            <div class="stat-foot" id="stat-per-hour">~0 / hour</div>
        </div>

        <div class="stat-card lime">
            <div class="stat-ic"><i class="fa-solid fa-gamepad"></i></div>
            <span class="stat-label">Matches Done</span>
            <div class="stat-value" id="stat-completed">0</div>
            <div class="stat-foot" id="stat-active-matches">0 Active</div>
        </div>

        <div class="stat-card pink">
            <div class="stat-ic"><i class="fa-solid fa-arrow-trend-up"></i></div>
            <span class="stat-label">Total EXP</span>
            <div class="stat-value" id="stat-exp">+0</div>
            <div class="stat-foot" id="stat-exp-rate">~0 EXP/hr</div>
        </div>

        <div class="stat-card amber">
            <div class="stat-ic"><i class="fa-solid fa-clock"></i></div>
            <span class="stat-label">Uptime</span>
            <div class="stat-value" id="stat-uptime">00:00:00</div>
            <div class="stat-foot">100% Operational</div>
        </div>
    </section>

    <!-- WORKSPACE -->

    <section class="workspace">

        <!-- ACCOUNTS PANEL -->

        <div class="panel mobile-tab active" id="tab-accounts">
            <div class="panel-head">
                <div class="panel-title">
                    <div class="panel-ic"><i class="fa-solid fa-layer-group"></i></div>
                    <h3>
                        Account Command
                        <span class="chip" id="badge-count">0</span>
                    </h3>
                </div>
                <button class="btn" id="btn-pause-all" onclick="togglePauseAll()">
                    <i class="fa-solid fa-pause"></i>
                    <span class="hide-sm">Pause All</span>
                </button>
            </div>

            <div class="controls">
                <div class="search">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input
                        id="account-search"
                        type="text"
                        placeholder="Search nickname or UID..."
                        oninput="filterAccounts()"
                    >
                </div>
                <div class="filters">
                    <button class="filter active" onclick="setFilter('all',this)">ALL</button>
                    <button class="filter" onclick="setFilter('in_match',this)">MATCH</button>
                    <button class="filter" onclick="setFilter('online',this)">ONLINE</button>
                    <button class="filter" onclick="setFilter('paused',this)">PAUSED</button>
                </div>
            </div>

            <div class="accounts-wrap" id="accounts-container">
                <div class="empty-state">
                    <i class="fa-solid fa-circle-notch fa-spin"></i>
                    <p>Initializing Command Center...</p>
                </div>
            </div>
        </div>

        <!-- CONSOLE PANEL -->

        <div class="panel console-panel mobile-tab" id="tab-console">
            <div class="panel-head">
                <div class="panel-title">
                    <div class="panel-ic"><i class="fa-solid fa-terminal"></i></div>
                    <h3>Live Console</h3>
                </div>
                <button class="btn" onclick="clearLogs()">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>

            <div class="console-tools">
                <div class="console-filters">
                    <button class="cfilter active" onclick="setLogFilter('all',this)">ALL</button>
                    <button class="cfilter" onclick="setLogFilter('match',this)">MATCH</button>
                    <button class="cfilter" onclick="setLogFilter('success',this)">EXP</button>
                    <button class="cfilter" onclick="setLogFilter('error',this)">ERRORS</button>
                </div>
                <button class="cfilter active" id="btn-autoscroll" onclick="toggleAutoScroll()">
                    <i class="fa-solid fa-arrows-down-to-line"></i>
                </button>
            </div>

            <div class="console-body" id="console-stream" onscroll="handleLogScroll()"></div>

            <div class="console-foot">
                <span class="live-tag">
                    <span class="dot" style="width:6px;height:6px;border-radius:50%;background:var(--neon-lime);box-shadow:0 0 12px var(--neon-lime);animation:dotPulse 1.4s infinite;"></span>
                    Live Stream
                </span>
                <span>TOXIC LEVEL UP • Premium Engine</span>
            </div>
        </div>

        <!-- MOBILE STATS TAB -->

        <div class="panel mobile-tab" id="tab-stats">
            <div class="panel-head">
                <div class="panel-title">
                    <div class="panel-ic"><i class="fa-solid fa-chart-line"></i></div>
                    <h3>Engine Analytics</h3>
                </div>
            </div>

            <div style="padding:18px">
                <div class="stat-card violet" style="margin-bottom:14px">
                    <span class="stat-label">Matches Started</span>
                    <div class="stat-value" id="m-started">0</div>
                    <div class="stat-foot" id="m-rate">~0 / hour</div>
                </div>

                <div class="stat-card lime" style="margin-bottom:14px">
                    <span class="stat-label">Total EXP</span>
                    <div class="stat-value" id="m-exp">+0</div>
                    <div class="stat-foot" id="m-exp-rate">~0 EXP/hr</div>
                </div>

                <div class="stat-card" style="margin-bottom:14px">
                    <span class="stat-label">System Status</span>
                    <div class="stat-value" style="color:var(--neon-lime); font-size:20px">
                        <i class="fa-solid fa-shield-halved"></i> Operational
                    </div>
                    <div class="stat-foot">Command Center Running</div>
                </div>
            </div>
        </div>

    </section>
</div>

<!-- MOBILE NAV -->

<nav class="mobile-nav">
    <button class="nav-btn active" onclick="switchTab('accounts',this)">
        <i class="fa-solid fa-users"></i>
        Accounts
    </button>
    <button class="nav-btn" onclick="switchTab('stats',this)">
        <i class="fa-solid fa-chart-pie"></i>
        Stats
    </button>
    <button class="nav-btn" onclick="switchTab('console',this)">
        <i class="fa-solid fa-terminal"></i>
        Console
    </button>
    <button class="nav-btn" onclick="openAddModal()">
        <i class="fa-solid fa-circle-plus" style="color:var(--neon-cyan)"></i>
        Add
    </button>
</nav>

<!-- ADD MODAL -->

<div class="modal-bg" id="add-modal">
    <div class="modal-card">
        <div class="modal-head">
            <h3><i class="fa-solid fa-user-plus"></i>Add Account</h3>
            <button class="modal-close" onclick="closeAddModal()">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>

        <form onsubmit="submitAddAccount(event)">
            <div class="field-block">
                <label>Login Type</label>
                <select class="field-select" id="acc-type" onchange="toggleFormType()">
                    <option value="guest">Guest Account (UID + Password)</option>
                    <option value="token">Access Token</option>
                </select>
            </div>

            <div id="guest-inputs">
                <div class="field-block">
                    <label>Guest UID</label>
                    <input id="acc-uid" class="field-input" type="text" placeholder="Enter UID" autocomplete="off">
                </div>
                <div class="field-block">
                    <label>Guest Password / Key</label>
                    <input id="acc-password" class="field-input" type="text" placeholder="Enter password" autocomplete="off">
                </div>
            </div>

            <div id="token-inputs" style="display:none">
                <div class="field-block">
                    <label>Access Token</label>
                    <textarea id="acc-token" class="field-textarea" placeholder="Paste access token here..."></textarea>
                </div>
            </div>

            <div class="modal-actions">
                <button type="button" class="btn" onclick="closeAddModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">
                    <i class="fa-solid fa-rocket"></i>Save & Start
                </button>
            </div>
        </form>
    </div>
</div>

</div>

<script>

/* ============================================
   CONFIG
============================================ */

let ACCESS_KEY = localStorage.getItem("access_key") || "";
let IS_ADMIN = false;
let USER_NAME = "";

const EXP_TABLE = {
1:0,2:48,3:202,4:544,5:1012,6:1844,7:2792,8:3800,9:4870,10:6004,
11:7192,12:8448,13:9760,14:11140,15:12566,16:14060,17:15610,18:17224,19:18902,20:20632,
21:22424,22:24278,23:26192,24:28166,25:30200,26:32294,27:34448,28:37804,29:41274,30:44870,
31:48582,32:53394,33:58566,34:64096,35:69994,36:76460,37:83506,38:91128,39:99322,40:108092,
41:120144,42:133266,43:147472,44:162760,45:179126,46:196572,47:215368,48:235516,49:257010,50:279860,
51:304056,52:348318,53:394982,54:444044,55:495508,56:549364,57:633756,58:721744,59:813336,60:908522,
61:1041438,62:1180352,63:1325266,64:1476184,65:1634300,66:1840946,67:2056594,68:2281242,69:2514880,70:2757530,
71:3059506,72:3372284,73:3699456,74:4041030,75:4397002,76:4829104,77:5282204,78:5756304,79:6251408,80:6776502,
81:7381324,82:8043154,83:8752982,84:9510808,85:10316338,86:11277190,87:12291748,88:13360304,89:14482858,90:15659418,
91:17026708,92:18453950,93:19941280,94:21488570,95:23095858,96:24763138,97:26490428,98:28378704,99:30124996,100:32032884
};

let cachedAccounts = [];
let cachedLogs = [];
let activeFilter = "all";
let activeLogFilter = "all";
let autoScroll = true;
let clientStart = Date.now();

/* ============================================
   LOGIN
============================================ */

async function login(e){
    e.preventDefault();
    const inp = document.getElementById("login-key");
    const err = document.getElementById("login-error");
    const key = inp.value.trim();

    if(!key){
        err.innerText = "✕ Access key is required";
        return;
    }

    // Show loading state
    const btn = document.querySelector(".login-btn");
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying...';
    btn.disabled = true;

    try{
        const res = await fetch("/api/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({access_key: key})
        });

        const data = await res.json();

        if(data.status === "ok"){
            // Save credentials
            ACCESS_KEY = key;
            IS_ADMIN = data.is_admin;
            USER_NAME = data.name;
            localStorage.setItem("access_key", key);
            localStorage.setItem("is_admin", data.is_admin);
            localStorage.setItem("user_name", data.name);

            err.innerText = "";
            const sc = document.getElementById("login-screen");
            sc.style.transition = "opacity .4s";
            sc.style.opacity = "0";
            setTimeout(()=>{
                sc.style.display = "none";
                document.getElementById("app").style.display = "block";
                fetchStats();
                toast(`Welcome to Command Center, ${USER_NAME || "User"}`, "success");
            }, 400);
        } else {
            err.innerText = "✕ " + (data.error || "Invalid access key");
            inp.value = "";
            inp.animate([
                {transform:"translateX(-8px)"},
                {transform:"translateX(8px)"},
                {transform:"translateX(-5px)"},
                {transform:"translateX(0)"}
            ], {duration:300});
        }
    } catch(err_){
        err.innerText = "✕ Connection error";
        console.error(err_);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Helper function to add access key to all API requests
function getAuthHeaders(){
    return {
        "Content-Type": "application/json",
        "X-Access-Key": ACCESS_KEY
    };
}

function logout(){
    localStorage.removeItem("access_key");
    localStorage.removeItem("is_admin");
    localStorage.removeItem("user_name");
    ACCESS_KEY = "";
    IS_ADMIN = false;
    USER_NAME = "";
    location.reload();
}

// Show admin button if user is admin
if(IS_ADMIN){
    document.getElementById("admin-btn").style.display = "inline-flex";
}

// Admin Panel Functions
async function openAdminPanel(){
    if(!IS_ADMIN){
        toast("Admin access required", "error");
        return;
    }

    const modal = document.createElement("div");
    modal.className = "modal-bg active";
    modal.innerHTML = `
        <div class="modal-card" style="max-width:600px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-user-shield"></i> Admin Panel</h3>
                <button class="modal-close" onclick="this.closest('.modal-bg').remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="admin-section">
                    <h4>Create New Access Key</h4>
                    <div class="field-wrap">
                        <input id="new-key-name" class="key-input" placeholder="User Name" style="padding:12px 20px;">
                    </div>
                    <div class="field-wrap">
                        <label>
                            <input type="checkbox" id="new-key-admin"> Admin privileges
                        </label>
                    </div>
                    <button class="btn btn-primary" onclick="createNewKey()">Create Key</button>
                </div>
                <div class="admin-section" style="margin-top:20px;">
                    <h4>Existing Keys</h4>
                    <div id="keys-list" style="max-height:300px;overflow-y:auto;">
                        <div class="loading">Loading...</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    loadAccessKeys();
}

async function loadAccessKeys(){
    try{
        const r = await fetch("/api/admin/keys", {
            headers: getAuthHeaders()
        });
        const d = await r.json();
        if(d.status === "ok"){
            const list = document.getElementById("keys-list");
            if(!list) return;
            
            if(d.keys.length === 0){
                list.innerHTML = "<div class='text-muted'>No keys found</div>";
                return;
            }

            list.innerHTML = d.keys.map(k => `
                <div class="key-item" style="padding:12px;border:1px solid rgba(255,255,255,0.1);border-radius:8px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-weight:700;color:var(--neon-cyan);">${k.key}</div>
                        <div style="font-size:11px;color:var(--text-dim);">${k.name} ${k.is_admin ? '<span style="color:var(--neon-pink);">• ADMIN</span>' : ''}</div>
                    </div>
                    ${k.key !== "TOXIC2" ? `<button class="btn" style="padding:6px 12px;font-size:11px;" onclick="deleteKey('${k.key}')">Delete</button>` : '<span style="font-size:11px;color:var(--text-muted);">Default</span>'}
                </div>
            `).join("");
        }
    } catch(e){
        console.error(e);
        toast("Failed to load keys", "error");
    }
}

async function createNewKey(){
    const name = document.getElementById("new-key-name").value.trim();
    const isAdmin = document.getElementById("new-key-admin").checked;

    if(!name){
        toast("Name is required", "error");
        return;
    }

    try{
        const r = await fetch("/api/admin/keys/create", {
            method:"POST",
            headers:getAuthHeaders(),
            body:JSON.stringify({name, is_admin:isAdmin})
        });
        const d = await r.json();
        if(d.status === "ok"){
            toast(`Key created: ${d.key}`, "success");
            document.getElementById("new-key-name").value = "";
            document.getElementById("new-key-admin").checked = false;
            loadAccessKeys();
        } else {
            toast(d.error || "Failed to create key", "error");
        }
    } catch(e){
        console.error(e);
        toast("Failed to create key", "error");
    }
}

async function deleteKey(key){
    if(!confirm(`Delete key ${key}?`)) return;

    try{
        const r = await fetch("/api/admin/keys/delete", {
            method:"POST",
            headers:getAuthHeaders(),
            body:JSON.stringify({key})
        });
        const d = await r.json();
        if(d.status === "ok"){
            toast("Key deleted", "success");
            loadAccessKeys();
        } else {
            toast(d.error || "Failed to delete key", "error");
        }
    } catch(e){
        console.error(e);
        toast("Failed to delete key", "error");
    }
}

function toggleKey(){
    const inp = document.getElementById("login-key");
    const eye = document.getElementById("key-eye");
    if(inp.type === "password"){
        inp.type = "text";
        eye.className = "fa-solid fa-eye-slash";
    } else {
        inp.type = "password";
        eye.className = "fa-solid fa-eye";
    }
}

/* ============================================
   TOAST
============================================ */

function toast(msg, type="info"){
    const wrap = document.getElementById("toast-wrap");
    const t = document.createElement("div");
    t.className = "toast " + type;
    const icons = {success:"fa-circle-check", error:"fa-triangle-exclamation", info:"fa-circle-info"};
    t.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><span>${esc(msg)}</span>`;
    wrap.appendChild(t);
    setTimeout(()=>{
        t.style.opacity = "0";
        t.style.transform = "translateX(30px)";
        t.style.transition = ".3s";
        setTimeout(()=>t.remove(), 300);
    }, 3200);
}

/* ============================================
   MODAL
============================================ */

function openAddModal(){
    document.getElementById("add-modal").classList.add("active");
}

function closeAddModal(){
    document.getElementById("add-modal").classList.remove("active");
}

function toggleFormType(){
    const t = document.getElementById("acc-type").value;
    document.getElementById("guest-inputs").style.display = t === "guest" ? "block" : "none";
    document.getElementById("token-inputs").style.display = t === "token" ? "block" : "none";
}

/* ============================================
   ADD ACCOUNT
============================================ */

async function submitAddAccount(e){
    e.preventDefault();
    const type = document.getElementById("acc-type").value;
    let payload = {};

    if(type === "guest"){
        const uid = document.getElementById("acc-uid").value.trim();
        const pass = document.getElementById("acc-password").value.trim();
        if(!uid || !pass){ toast("UID and password required", "error"); return; }
        payload = {uid, password:pass};
    } else {
        const token = document.getElementById("acc-token").value.trim();
        if(!token){ toast("Access token required", "error"); return; }
        payload = {token};
    }

    try {
        const r = await fetch("/api/account/add", {
            method:"POST",
            headers:getAuthHeaders(),
            body:JSON.stringify(payload)
        });
        const d = await r.json();
        if(d.status === "ok"){
            closeAddModal();
            toast("Account added successfully", "success");
            fetchStats();
        } else {
            toast(d.error || "Failed to add account", "error");
        }
    } catch(err){
        toast("Network error", "error");
    }
}

/* ============================================
   DELETE
============================================ */

async function deleteAccount(uid, authUid=""){
    if(!confirm(`Remove account ${uid}?`)) return;
    try {
        const r = await fetch("/api/account/delete", {
            method:"POST",
            headers:getAuthHeaders(),
            body:JSON.stringify({uid, auth_uid:authUid})
        });
        const d = await r.json();
        if(d.status === "ok"){
            toast("Account removed", "success");
            const c = document.getElementById("acc-"+uid);
            if(c) c.remove();
            fetchStats();
        } else {
            toast(d.error || "Delete failed", "error");
        }
    } catch(e){
        toast("Network error", "error");
    }
}

/* ============================================
   ACCOUNT ACTIONS
============================================ */

async function refreshAcc(uid){
    try {
        toast(`Refreshing ${uid}...`, "info");
        await fetch("/api/account/refresh", {
            method:"POST",
            headers:getAuthHeaders(),
            body:JSON.stringify({uid})
        });
        setTimeout(fetchStats, 800);
    } catch(e){ toast("Refresh failed", "error"); }
}

async function restartAcc(uid){
    try {
        toast(`Restarting ${uid}...`, "info");
        await fetch("/api/account/restart", {
            method:"POST",
            headers:getAuthHeaders(),
            body:JSON.stringify({uid})
        });
        setTimeout(fetchStats, 800);
    } catch(e){ toast("Restart failed", "error"); }
}

async function togglePause(uid){
    try {
        const r = await fetch("/api/account/pause", {
            method:"POST",
            headers:getAuthHeaders(),
            body:JSON.stringify({uid})
        });
        const d = await r.json();
        if(d.status === "ok"){
            toast(d.is_paused ? `Paused ${uid}` : `Resumed ${uid}`, d.is_paused ? "info" : "success");
            fetchStats();
        } else {
            toast(d.error || "Pause failed", "error");
        }
    } catch(e){ toast("Network error", "error"); }
}

async function togglePauseAll(){
    try {
        const r = await fetch("/api/account/pause_all", {
            method:"POST",
            headers:getAuthHeaders()
        });
        const d = await r.json();
        if(d.status === "ok"){
            toast(d.all_paused ? "All accounts paused" : "All accounts resumed", d.all_paused ? "info" : "success");
            fetchStats();
        } else {
            toast(d.error || "Failed", "error");
        }
    } catch(e){ toast("Network error", "error"); }
}

/* ============================================
   FILTER
============================================ */

function setFilter(f, btn){
    activeFilter = f;
    document.querySelectorAll(".filter").forEach(x=>x.classList.remove("active"));
    if(btn) btn.classList.add("active");
    filterAccounts();
}

function filterAccounts(){
    const q = (document.getElementById("account-search").value || "").toLowerCase().trim();
    document.querySelectorAll(".account-card").forEach(card=>{
        const uid = (card.dataset.uid || "").toLowerCase();
        const nick = (card.dataset.nick || "").toLowerCase();
        const st = (card.dataset.status || "").toLowerCase();
        const paused = card.dataset.paused === "1";

        const matchSearch = !q || uid.includes(q) || nick.includes(q);
        let matchFilter = true;

        if(activeFilter === "in_match") matchFilter = st.includes("match") && !paused;
        else if(activeFilter === "online") matchFilter = (st.includes("online") || st.includes("searching")) && !paused;
        else if(activeFilter === "paused") matchFilter = paused || st.includes("paused");

        card.style.display = matchSearch && matchFilter ? "block" : "none";
    });
}

/* ============================================
   RENDER ACCOUNTS
============================================ */

function renderAccounts(accounts){
    const container = document.getElementById("accounts-container");
    document.getElementById("badge-count").innerText = accounts.length;

    const allPaused = accounts.length > 0 && accounts.every(a=>a.is_paused || a.status === "PAUSED");
    const pb = document.getElementById("btn-pause-all");
    pb.innerHTML = allPaused
        ? '<i class="fa-solid fa-play"></i><span class="hide-sm">Resume All</span>'
        : '<i class="fa-solid fa-pause"></i><span class="hide-sm">Pause All</span>';

    if(accounts.length === 0){
        container.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-ghost"></i>
                <p>No accounts yet</p>
                <button class="btn btn-primary" onclick="openAddModal()">
                    <i class="fa-solid fa-plus"></i> Add First Account
                </button>
            </div>`;
        return;
    }

    if(container.querySelector(".empty-state")) container.innerHTML = "";

    const uids = new Set(accounts.map(a=>String(a.uid)));
    container.querySelectorAll(".account-card").forEach(c=>{
        if(!uids.has(c.dataset.uid)) c.remove();
    });

    accounts.forEach(acc=>{
        const uid = String(acc.uid);
        const level = Math.max(1, parseInt(acc.level) || 1);
        const nextLvl = Math.min(100, level + 1);
        const baseExp = EXP_TABLE[level] ?? 0;
        const targetExp = EXP_TABLE[nextLvl] ?? baseExp + 50000;
        const needed = Math.max(1, targetExp - baseExp);
        const curExp = Number(acc.current_exp || 0);
        const earned = Math.max(0, curExp - baseExp);
        const remaining = Math.max(0, targetExp - curExp);
        const pct = level >= 100 ? 100 : Math.min(100, Math.max(0, earned / needed * 100));

        const paused = Boolean(acc.is_paused || acc.status === "PAUSED");
        const status = paused ? "PAUSED" : (acc.status || "ONLINE");

        let cls = "status-online";
        if(paused) cls = "status-paused";
        else if(status === "IN_MATCH") cls = "status-match";
        else if(status === "SEARCHING") cls = "status-search";
        else if(status !== "ONLINE") cls = "status-error";

        const stText = paused
            ? "PAUSED"
            : status === "IN_MATCH"
            ? `IN MATCH (${acc.active_matches || 1})`
            : status;

        let card = document.getElementById("acc-" + uid);
        if(!card){
            card = document.createElement("div");
            card.id = "acc-" + uid;
            card.className = "account-card";
            container.appendChild(card);
        }

        card.dataset.uid = uid;
        card.dataset.nick = acc.nickname || "";
        card.dataset.status = cls.replace("status-", "");
        card.dataset.paused = paused ? "1" : "0";

        card.innerHTML = `
            <div class="acc-head">
                <div class="acc-id">
                    <div class="acc-avatar">
                        <div class="acc-avatar-ring"></div>
                        <div class="acc-avatar-core"><i class="fa-solid fa-gamepad"></i></div>
                        <span class="acc-level">L${level}</span>
                    </div>
                    <div style="min-width:0">
                        <div class="acc-name">
                            ${esc(acc.nickname || "Unknown")}
                            <span class="acc-region">${esc(acc.region || "BD")}</span>
                        </div>
                        <div class="acc-uid">
                            <span>UID: ${esc(uid)}</span>
                            <button class="copy-btn" onclick="copyUid('${escAttr(uid)}')" title="Copy">
                                <i class="fa-regular fa-copy"></i>
                            </button>
                            <span class="acc-uptime" data-uid="${escAttr(uid)}" data-uptime="${Math.floor(acc.uptime_seconds || 0)}" data-paused="${paused ? 1 : 0}">
                                <i class="fa-solid fa-stopwatch"></i>
                                ${fmtDur(acc.uptime_seconds || 0)}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="status-pill ${cls}">
                    <span class="sdot"></span>${stText}
                </div>
            </div>

            <div class="acc-metrics">
                <div class="metric-box">
                    <span>Initial</span>
                    <strong>${Number(acc.initial_exp || 0).toLocaleString()}</strong>
                </div>
                <div class="metric-box">
                    <span>Current</span>
                    <strong>${curExp.toLocaleString()}</strong>
                </div>
                <div class="metric-box gain">
                    <span>Gained</span>
                    <strong>+${Number(acc.gained_exp || 0).toLocaleString()}</strong>
                </div>
            </div>

            <div class="progress-block">
                <div class="progress-top">
                    <span>LEVEL ${level} → <b>L${nextLvl}</b></span>
                    <b>${remaining.toLocaleString()} EXP LEFT</b>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:${pct.toFixed(1)}%"></div>
                </div>
                <div class="progress-bot">
                    <span>${earned.toLocaleString()} / ${needed.toLocaleString()}</span>
                    <span class="pct">${pct.toFixed(1)}%</span>
                </div>
            </div>

            <div class="acc-foot">
                <span class="acc-time">
                    <i class="fa-regular fa-clock"></i>
                    ${esc(acc.last_match_time || "Running...")}
                </span>
                <div class="acc-actions">
                    <button class="act-btn" onclick="togglePause('${escAttr(uid)}')" title="${paused ? "Resume" : "Pause"}">
                        <i class="fa-solid ${paused ? "fa-play" : "fa-pause"}"></i>
                    </button>
                    <button class="act-btn" onclick="restartAcc('${escAttr(uid)}')" title="Restart">
                        <i class="fa-solid fa-rotate-right"></i>
                    </button>
                    <button class="act-btn" onclick="refreshAcc('${escAttr(uid)}')" title="Refresh">
                        <i class="fa-solid fa-arrows-rotate"></i>
                    </button>
                    <button class="act-btn danger" onclick="deleteAccount('${escAttr(uid)}', '${escAttr(acc.auth_uid || "")}')" title="Delete">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>`;
    });

    filterAccounts();
}

/* ============================================
   LOGS
============================================ */

function setLogFilter(f, btn){
    activeLogFilter = f;
    document.querySelectorAll(".cfilter").forEach(x=>{
        if(x.id !== "btn-autoscroll") x.classList.remove("active");
    });
    if(btn) btn.classList.add("active");
    renderLogs(cachedLogs);
}

function renderLogs(logs){
    const stream = document.getElementById("console-stream");
    let list = logs || [];

    if(activeLogFilter === "match"){
        list = list.filter(l => String(l.message || "").toLowerCase().includes("match"));
    } else if(activeLogFilter === "success"){
        list = list.filter(l => l.level === "success" || String(l.message || "").includes("EXP"));
    } else if(activeLogFilter === "error"){
        list = list.filter(l => l.level === "error" || l.level === "warning");
    }

    stream.innerHTML = list.map(l=>`
        <div class="log-line">
            <span class="log-ts">[${esc(l.time || "00:00:00")}]</span>
            <span class="log-msg ${l.level || "info"}">${esc(l.message || "")}</span>
        </div>
    `).join("");

    if(autoScroll) stream.scrollTop = stream.scrollHeight;
}

async function clearLogs(){
    try {
        await fetch("/api/logs/clear", {
            method:"POST",
            headers:getAuthHeaders()
        });
        cachedLogs = [];
        renderLogs([]);
        toast("Console cleared", "info");
    } catch(e){ toast("Clear failed", "error"); }
}

function toggleAutoScroll(){
    autoScroll = !autoScroll;
    document.getElementById("btn-autoscroll").classList.toggle("active", autoScroll);
    if(autoScroll) document.getElementById("console-stream").scrollTop = 999999;
}

function handleLogScroll(){
    const s = document.getElementById("console-stream");
    if(s.scrollHeight - s.scrollTop - s.clientHeight > 80) autoScroll = false;
}

/* ============================================
   FETCH STATS
============================================ */

async function fetchStats(){
    try {
        const r = await fetch("/api/stats", {
            headers: getAuthHeaders()
        });
        if(!r.ok) throw new Error("HTTP " + r.status);
        const d = await r.json();

        const accs = Array.isArray(d.accounts) ? d.accounts : [];
        const logs = Array.isArray(d.logs) ? d.logs : [];

        setText("stat-accounts", d.total_accounts ?? accs.length);
        setText("stat-started", d.total_matches_started || 0);
        setText("stat-completed", d.total_matches || 0);
        setText("stat-exp", "+" + Number(d.total_gained_exp || 0).toLocaleString());
        setText("stat-active-matches", (d.total_active_matches || 0) + " Active");

        const online = accs.filter(a => a.status === "ONLINE" || a.status === "IN_MATCH").length;
        setText("stat-online", online + " Online");

        // Per hour calc
        const uptimeH = Math.max(0.016, (d.uptime || 60) / 3600);
        const perH = Math.round((d.total_matches_started || 0) / uptimeH);
        setText("stat-per-hour", "~" + perH + " / hour");

        setText("stat-exp-rate", "~" + Number(d.exp_per_hour || 0).toLocaleString() + " EXP/hr");

        // Mobile stats
        setText("m-started", d.total_matches_started || 0);
        setText("m-rate", "~" + perH + " / hour");
        setText("m-exp", "+" + Number(d.total_gained_exp || 0).toLocaleString());
        setText("m-exp-rate", "~" + Number(d.exp_per_hour || 0).toLocaleString() + " EXP/hr");

        cachedAccounts = accs;
        cachedLogs = logs;

        renderAccounts(accs);
        renderLogs(logs);

    } catch(e){
        console.warn("Stats fetch error:", e);
    }
}

/* ============================================
   COPY / HELPERS
============================================ */

function copyUid(uid){
    if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(uid).then(()=> toast("UID copied: " + uid, "success"));
    } else {
        toast("UID: " + uid, "info");
    }
}

function switchTab(name, btn){
    document.querySelectorAll(".nav-btn").forEach(x=>x.classList.remove("active"));
    if(btn) btn.classList.add("active");
    document.querySelectorAll(".mobile-tab").forEach(x=>x.classList.remove("active"));
    const el = document.getElementById("tab-" + name);
    if(el) el.classList.add("active");
}

function setText(id, v){
    const el = document.getElementById(id);
    if(el) el.innerText = v ?? "";
}

function esc(s){
    if(s === null || s === undefined) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");
}

function escAttr(s){ return esc(s); }

function fmtDur(sec){
    sec = Math.max(0, Math.floor(Number(sec) || 0));
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    if(h > 0) return `${h}h ${String(m).padStart(2,"0")}m`;
    return `${String(m).padStart(2,"0")}m ${String(s).padStart(2,"0")}s`;
}

function manualRefresh(){
    fetchStats();
    toast("Command Center refreshed", "info");
}

/* ============================================
   LIVE UPTIME
============================================ */

setInterval(()=>{
    const el = Math.floor((Date.now() - clientStart) / 1000);
    const h = String(Math.floor(el / 3600)).padStart(2, "0");
    const m = String(Math.floor((el % 3600) / 60)).padStart(2, "0");
    const s = String(el % 60).padStart(2, "0");
    setText("stat-uptime", `${h}:${m}:${s}`);

    document.querySelectorAll(".acc-uptime").forEach(u=>{
        if(u.dataset.paused === "1") return;
        let v = parseInt(u.dataset.uptime || "0") + 1;
        u.dataset.uptime = v;
        u.innerHTML = `<i class="fa-solid fa-stopwatch"></i>${fmtDur(v)}`;
    });
}, 1000);

/* ============================================
   ENTER KEY
============================================ */

document.getElementById("login-key").addEventListener("keydown", e=>{
    if(e.key === "Enter") login(e);
});

</script>
</body>
</html>"""


# ==================== AUTHENTICATION MIDDLEWARE ====================
async def auth_middleware(app, handler):
    """Authentication middleware for API endpoints"""
    async def middleware_handler(request):
        # Public endpoints that don't require authentication
        public_paths = ["/", "/api/login", "/api/status"]
        
        if request.path in public_paths:
            return await handler(request)
        
        # Check for access key in headers
        auth_header = request.headers.get("X-Access-Key", "")
        auth_query = request.query.get("access_key", "")
        access_key = auth_header or auth_query
        
        if not access_key:
            return web.json_response(
                {"status": "error", "error": "Access key required"},
                status=401
            )
        
        key_data = validate_access_key(access_key)
        if not key_data:
            return web.json_response(
                {"status": "error", "error": "Invalid access key"},
                status=403
            )
        
        # Add key data to request for use in handlers
        request["access_key"] = access_key
        request["key_data"] = key_data
        
        return await handler(request)
    
    return middleware_handler


# ==================== HTTP HANDLERS ====================

async def handle_login(request: web.Request) -> web.Response:
    """Handle login with access key"""
    try:
        data = await request.json()
        access_key = str(data.get("access_key", "")).strip()
        
        if not access_key:
            return web.json_response(
                {"status": "error", "error": "Access key is required"},
                status=400
            )
        
        key_data = validate_access_key(access_key)
        if not key_data:
            return web.json_response(
                {"status": "error", "error": "Invalid access key"},
                status=401
            )
        
        return web.json_response({
            "status": "ok",
            "key": key_data["key"],
            "is_admin": key_data.get("is_admin", False),
            "name": key_data.get("name", "")
        })
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=500)


async def handle_status(request: web.Request) -> web.Response:
    """Public status endpoint"""
    return web.json_response({
        "status": "running",
        "version": "1.0.0",
        "auth_required": True
    })


async def handle_index(request: web.Request) -> web.Response:
    content = FALLBACK_INDEX_HTML
    candidate_paths = [
        TEMPLATE_PATH,
        os.path.join(os.getcwd(), "templates", "index.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"),
        "templates/index.html",
        "index.html",
        "/opt/render/project/src/templates/index.html",
        "/app/templates/index.html"
    ]
    for p in candidate_paths:
        if p and os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()
                    break
            except Exception:
                pass
    return web.Response(text=content, content_type="text/html", charset="utf-8")


async def handle_get_stats(request: web.Request) -> web.Response:
    accounts_data = list(bot_state.accounts.values())
    accounts_data.sort(key=lambda x: x.get("gained_exp", 0), reverse=True)
    uptime_sec = max(1, int(time.time() - bot_state.start_time))
    total_gained = bot_state.total_gained_exp
    exp_per_hour = int((total_gained / uptime_sec) * 3600)
    total_active_matches = sum(acc.get("active_matches", 0) for acc in accounts_data)

    for acc in accounts_data:
        uid_k = str(acc.get("uid", ""))
        acc["uptime_seconds"] = bot_state.get_account_uptime(uid_k)
        acc["is_paused"] = bot_state.is_paused(uid_k)

    return web.json_response({
        "total_accounts": len(bot_state.accounts),
        "total_matches": bot_state.total_matches,
        "total_matches_started": bot_state.total_matches_started,   # 🔥 NEW
        "total_active_matches": total_active_matches,
        "total_gained_exp": total_gained,
        "exp_per_hour": exp_per_hour,
        "accounts": accounts_data,
        "logs": bot_state.logs[-80:],
        "uptime": uptime_sec
    })


async def handle_add_account(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        accounts_file = "accounts.json"
        existing = []
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        if "uid" in data and "password" in data:
            uid = str(data["uid"]).strip()
            pwd = str(data["password"]).strip()
            if not uid or not pwd:
                return web.json_response({"status": "error", "error": "UID and Password are required"})

            # Cancel previous worker if already running for this UID
            if uid in bot_state.account_workers:
                try:
                    bot_state.account_workers[uid].cancel()
                except Exception:
                    pass
                bot_state.account_workers.pop(uid, None)

            existing = [acc for acc in existing if str(acc.get("uid", "")) != uid]
            existing.append({"uid": uid, "password": pwd})
            identifier = uid

        elif "token" in data:
            token = str(data["token"]).strip()
            if not token:
                return web.json_response({"status": "error", "error": "Token is required"})

            # Cancel worker if token prefix matches
            tok_key = token[:16]
            for k in list(bot_state.account_workers.keys()):
                if k == tok_key or k.startswith(tok_key[:10]) or tok_key.startswith(k[:10]):
                    try:
                        bot_state.account_workers[k].cancel()
                    except Exception:
                        pass
                    bot_state.account_workers.pop(k, None)

            existing = [acc for acc in existing if acc.get("token", "") != token]
            existing.append({"token": token})
            identifier = f"Token_{token[:8]}..."
        else:
            return web.json_response({"status": "error", "error": "Invalid payload"})

        with open(accounts_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

        bot_state.log(f"New account added to rotation: {identifier}", "success")
        
        # Trigger dynamic worker launch in Main.py
        if "on_account_added" in bot_state.refresh_callbacks:
            asyncio.create_task(bot_state.refresh_callbacks["on_account_added"](data))

        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)})


async def handle_delete_account(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        req_uid = str(data.get("uid", "")).strip()
        req_auth_uid = str(data.get("auth_uid", "")).strip()
        if not req_uid and not req_auth_uid:
            return web.json_response({"status": "error", "error": "UID is required"})

        # Collect ALL possible candidate identifiers for this account
        candidate_ids = set()
        if req_uid:
            candidate_ids.add(req_uid)
        if req_auth_uid:
            candidate_ids.add(req_auth_uid)

        # Check game_to_auth and auth_to_game mappings
        for cid in list(candidate_ids):
            if cid in bot_state.game_to_auth_id:
                candidate_ids.add(str(bot_state.game_to_auth_id[cid]))
            if cid in bot_state.auth_to_game_id:
                candidate_ids.add(str(bot_state.auth_to_game_id[cid]))

        # Inspect bot_state.accounts
        target_tokens = set()
        for cid in list(candidate_ids):
            acc_info = bot_state.accounts.get(cid, {})
            if acc_info:
                if acc_info.get("auth_uid"):
                    candidate_ids.add(str(acc_info["auth_uid"]))
                if acc_info.get("uid"):
                    candidate_ids.add(str(acc_info["uid"]))
                t = acc_info.get("token") or acc_info.get("access_token")
                if t:
                    target_tokens.add(str(t))

        # Inspect bot_state.account_credentials
        for cid in list(candidate_ids):
            creds = bot_state.account_credentials.get(cid, {})
            if creds:
                if creds.get("auth_uid"):
                    candidate_ids.add(str(creds["auth_uid"]))
                if creds.get("account_id"):
                    candidate_ids.add(str(creds["account_id"]))
                t = creds.get("token") or creds.get("access_token") or creds.get("auth_token")
                if t:
                    target_tokens.add(str(t))

        # Also clean token_cache.json if entries match
        token_cache_file = "token_cache.json"
        if os.path.exists(token_cache_file):
            try:
                with open(token_cache_file, "r", encoding="utf-8") as f:
                    tcache = json.load(f)
                dirty_cache = False
                for k, v in list(tcache.items()):
                    k_str = str(k)
                    v_acc_id = str(v.get("account_id", ""))
                    v_auth_uid = str(v.get("auth_uid", ""))
                    if k_str in candidate_ids or v_acc_id in candidate_ids or v_auth_uid in candidate_ids:
                        candidate_ids.add(k_str)
                        if v_acc_id:
                            candidate_ids.add(v_acc_id)
                        if v_auth_uid:
                            candidate_ids.add(v_auth_uid)
                        del tcache[k]
                        dirty_cache = True
                if dirty_cache:
                    with open(token_cache_file, "w", encoding="utf-8") as f:
                        json.dump(tcache, f, indent=2)
            except Exception:
                pass

        # Remove from accounts.json
        accounts_file = "accounts.json"
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                new_existing = []
                for acc in existing:
                    acc_uid = str(acc.get("uid", "")).strip()
                    acc_tok = str(acc.get("token", "")).strip()
                    is_match = False
                    if acc_uid and acc_uid in candidate_ids:
                        is_match = True
                    if acc_tok and (acc_tok in candidate_ids or acc_tok in target_tokens):
                        is_match = True
                    for tok in target_tokens:
                        if acc_tok and (acc_tok.startswith(tok[:16]) or tok.startswith(acc_tok[:16])):
                            is_match = True
                    if not is_match:
                        new_existing.append(acc)

                with open(accounts_file, "w", encoding="utf-8") as f:
                    json.dump(new_existing, f, indent=2)
            except Exception:
                pass

        # Remove matching devices from devices.json
        devices_file = "devices.json"
        if os.path.exists(devices_file):
            try:
                with open(devices_file, "r", encoding="utf-8") as f:
                    devices_data = json.load(f)
                dirty_devices = False
                for dev_k in list(devices_data.keys()):
                    dev_k_str = str(dev_k)
                    if dev_k_str in candidate_ids:
                        del devices_data[dev_k]
                        dirty_devices = True
                    else:
                        for tok in target_tokens:
                            if dev_k_str == tok[:16] or tok.startswith(dev_k_str):
                                del devices_data[dev_k]
                                dirty_devices = True
                                break
                if dirty_devices:
                    with open(devices_file, "w", encoding="utf-8") as f:
                        json.dump(devices_data, f, indent=4)
            except Exception:
                pass

        # Remove from in-memory bot_state.accounts & credentials
        for cid in candidate_ids:
            bot_state.accounts.pop(cid, None)
            bot_state.account_credentials.pop(cid, None)
            bot_state.auth_to_game_id.pop(cid, None)
            bot_state.game_to_auth_id.pop(cid, None)
            bot_state.account_token_map.pop(cid, None)

        # Cancel matching worker tasks
        cancelled_keys = []
        for k, worker in list(bot_state.account_workers.items()):
            k_str = str(k)
            should_cancel = False
            if k_str in candidate_ids:
                should_cancel = True
            for tok in target_tokens:
                if k_str == tok[:16] or tok.startswith(k_str[:10]):
                    should_cancel = True
            if should_cancel:
                try:
                    worker.cancel()
                except Exception:
                    pass
                cancelled_keys.append(k)

        for k in cancelled_keys:
            bot_state.account_workers.pop(k, None)

        for cid in candidate_ids:
            bot_state.close_writers_for_account(cid)

        # Trigger on_account_deleted callback in Main.py if registered
        if "on_account_deleted" in bot_state.refresh_callbacks:
            try:
                asyncio.create_task(bot_state.refresh_callbacks["on_account_deleted"](list(candidate_ids)))
            except Exception:
                pass

        target_repr = req_uid or req_auth_uid
        bot_state.log(f"Account {target_repr} completely deleted from system and stopped.", "warning", target_repr)
        bot_state.recalc_totals()
        return web.json_response({"status": "ok", "deleted": list(candidate_ids)})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)})


async def handle_refresh_account(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        uid = str(data.get("uid", "")).strip()
        if "on_refresh_account" in bot_state.refresh_callbacks:
            asyncio.create_task(bot_state.refresh_callbacks["on_refresh_account"](uid))
        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)})


async def handle_restart_account(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        uid = str(data.get("uid", "")).strip()
        if "on_restart_account" in bot_state.refresh_callbacks:
            asyncio.create_task(bot_state.refresh_callbacks["on_restart_account"](uid))
        elif "on_refresh_account" in bot_state.refresh_callbacks:
            asyncio.create_task(bot_state.refresh_callbacks["on_refresh_account"](uid))
        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)})


async def handle_clear_logs(request: web.Request) -> web.Response:
    bot_state.logs.clear()
    return web.json_response({"status": "ok"})


async def handle_toggle_pause(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        uid = str(data.get("uid", "")).strip()
        if not uid:
            return web.json_response({"status": "error", "error": "UID is required"})
        is_paused = bot_state.toggle_pause(uid)
        return web.json_response({"status": "ok", "is_paused": is_paused})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)})


async def handle_toggle_pause_all(request: web.Request) -> web.Response:
    try:
        paused_state = bot_state.toggle_pause_all()
        return web.json_response({"status": "ok", "all_paused": paused_state})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)})


# ==================== ADMIN PANEL HANDLERS ====================
async def handle_list_keys(request: web.Request) -> web.Response:
    """List all access keys (admin only)"""
    try:
        access_key = request.get("access_key", "")
        if not is_admin_key(access_key):
            return web.json_response(
                {"status": "error", "error": "Admin access required"},
                status=403
            )
        
        keys = list_access_keys(access_key)
        return web.json_response({"status": "ok", "keys": keys})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=500)


async def handle_create_key(request: web.Request) -> web.Response:
    """Create a new access key (admin only)"""
    try:
        access_key = request.get("access_key", "")
        if not is_admin_key(access_key):
            return web.json_response(
                {"status": "error", "error": "Admin access required"},
                status=403
            )
        
        data = await request.json()
        name = str(data.get("name", "")).strip()
        is_admin = data.get("is_admin", False)
        
        if not name:
            return web.json_response(
                {"status": "error", "error": "Name is required"},
                status=400
            )
        
        created_by = request["key_data"].get("name", "admin")
        new_key = create_access_key(name, is_admin, created_by)
        
        if new_key:
            bot_state.log(f"New access key created: {new_key} ({name})", "info")
            return web.json_response({
                "status": "ok",
                "key": new_key,
                "name": name,
                "is_admin": is_admin
            })
        else:
            return web.json_response(
                {"status": "error", "error": "Failed to create key"},
                status=500
            )
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=500)


async def handle_delete_key(request: web.Request) -> web.Response:
    """Delete an access key (admin only)"""
    try:
        access_key = request.get("access_key", "")
        if not is_admin_key(access_key):
            return web.json_response(
                {"status": "error", "error": "Admin access required"},
                status=403
            )
        
        data = await request.json()
        key_to_delete = str(data.get("key", "")).strip()
        
        if not key_to_delete:
            return web.json_response(
                {"status": "error", "error": "Key is required"},
                status=400
            )
        
        success = delete_access_key(key_to_delete, access_key)
        
        if success:
            bot_state.log(f"Access key deleted: {key_to_delete}", "warning")
            return web.json_response({"status": "ok"})
        else:
            return web.json_response(
                {"status": "error", "error": "Failed to delete key (may be default admin)"},
                status=400
            )
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=500)


async def start_web_dashboard(host: str = "0.0.0.0", port: int = 5000):
    app = web.Application(middlewares=[auth_middleware])
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/status", handle_status)
    app.router.add_post("/api/login", handle_login)
    app.router.add_get("/api/stats", handle_get_stats)
    app.router.add_post("/api/account/add", handle_add_account)
    app.router.add_post("/api/account/delete", handle_delete_account)
    app.router.add_post("/api/account/refresh", handle_refresh_account)
    app.router.add_post("/api/account/restart", handle_restart_account)
    app.router.add_post("/api/account/pause", handle_toggle_pause)
    app.router.add_post("/api/account/pause_all", handle_toggle_pause_all)
    app.router.add_post("/api/logs/clear", handle_clear_logs)
    # Admin panel routes
    app.router.add_get("/api/admin/keys", handle_list_keys)
    app.router.add_post("/api/admin/keys/create", handle_create_key)
    app.router.add_post("/api/admin/keys/delete", handle_delete_key)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    return runner
