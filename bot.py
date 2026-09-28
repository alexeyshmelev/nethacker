from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nethackers.contracts.bot import ArenaBot

_cache_root = Path(tempfile.gettempdir()) / "nethack_arena_submission_cache"
_cache_root.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", str(_cache_root / "xdg"))
os.environ.setdefault("NUMBA_CACHE_DIR", str(_cache_root / "numba"))

import importlib  # noqa: E402
import re  # noqa: E402

# identity -> variant package, chosen by public mean (see build_portfolio.py)
CHOICE = {
    "arc-dwa-law-fem": "autoascend",
    "arc-dwa-law-mal": "autoascend",
    "arc-gno-neu-fem": "autoascend",
    "arc-gno-neu-mal": "autoascend",
    "arc-hum-law-fem": "autoascend",
    "arc-hum-law-mal": "autoascend",
    "arc-hum-neu-fem": "autoascend",
    "arc-hum-neu-mal": "autoascend",
    "bar-hum-cha-fem": "pf_v41x",
    "bar-hum-cha-mal": "pf_v41x",
    "bar-hum-neu-fem": "pf_v36",
    "bar-hum-neu-mal": "pf_v37",
    "bar-orc-cha-fem": "pf_v38",
    "bar-orc-cha-mal": "pf_v41x",
    "cav-dwa-law-fem": "autoascend",
    "cav-dwa-law-mal": "autoascend",
    "cav-gno-neu-fem": "pf_v41x",
    "cav-gno-neu-mal": "pf_v41x",
    "cav-hum-law-fem": "pf_v38",
    "cav-hum-law-mal": "pf_v41x",
    "cav-hum-neu-fem": "pf_vk_s23",
    "cav-hum-neu-mal": "pf_vk_s23",
    "hea-gno-neu-fem": "autoascend",
    "hea-gno-neu-mal": "autoascend",
    "hea-hum-neu-fem": "autoascend",
    "hea-hum-neu-mal": "autoascend",
    "kni-hum-law-fem": "autoascend",
    "kni-hum-law-mal": "autoascend",
    "mon-hum-cha-fem": "autoascend",
    "mon-hum-cha-mal": "autoascend",
    "mon-hum-law-fem": "autoascend",
    "mon-hum-law-mal": "autoascend",
    "mon-hum-neu-fem": "autoascend",
    "mon-hum-neu-mal": "autoascend",
    "pri-elf-cha-fem": "autoascend",
    "pri-elf-cha-mal": "autoascend",
    "pri-hum-cha-fem": "autoascend",
    "pri-hum-cha-mal": "autoascend",
    "pri-hum-law-fem": "autoascend",
    "pri-hum-law-mal": "autoascend",
    "pri-hum-neu-fem": "autoascend",
    "pri-hum-neu-mal": "autoascend",
    "ran-elf-cha-fem": "autoascend",
    "ran-elf-cha-mal": "autoascend",
    "ran-gno-neu-fem": "autoascend",
    "ran-gno-neu-mal": "autoascend",
    "ran-hum-cha-fem": "autoascend",
    "ran-hum-cha-mal": "autoascend",
    "ran-hum-neu-fem": "autoascend",
    "ran-hum-neu-mal": "autoascend",
    "ran-orc-cha-fem": "autoascend",
    "ran-orc-cha-mal": "autoascend",
    "rog-hum-cha-fem": "autoascend",
    "rog-hum-cha-mal": "autoascend",
    "rog-orc-cha-fem": "autoascend",
    "rog-orc-cha-mal": "autoascend",
    "sam-hum-law-fem": "s8ce023a",
    "sam-hum-law-mal": "s8ce023a",
    "tou-hum-neu-fem": "autoascend",
    "tou-hum-neu-mal": "autoascend",
    "val-dwa-law-fem": "autoascend",
    "val-hum-law-fem": "autoascend",
    "val-hum-neu-fem": "autoascend",
    "wiz-elf-cha-fem": "autoascend",
    "wiz-elf-cha-mal": "autoascend",
    "wiz-gno-neu-fem": "autoascend",
    "wiz-gno-neu-mal": "autoascend",
    "wiz-hum-cha-fem": "autoascend",
    "wiz-hum-cha-mal": "autoascend",
    "wiz-hum-neu-fem": "autoascend",
    "wiz-hum-neu-mal": "autoascend",
    "wiz-orc-cha-fem": "autoascend",
    "wiz-orc-cha-mal": "autoascend"
}
DEFAULT = "autoascend"
_ROLES = {"Archeologist": "arc", "Barbarian": "bar", "Caveman": "cav", "Cavewoman": "cav", "Healer": "hea",
          "Knight": "kni", "Monk": "mon", "Priest": "pri", "Priestess": "pri", "Ranger": "ran", "Rogue": "rog",
          "Samurai": "sam", "Tourist": "tou", "Valkyrie": "val", "Wizard": "wiz"}
_RACES = {"human": "hum", "elven": "elf", "dwarven": "dwa", "gnomish": "gno", "orcish": "orc"}
_ALIGNS = {"lawful": "law", "neutral": "neu", "chaotic": "cha"}
_RE = re.compile(r"You are an? (lawful|neutral|chaotic) (?:(male|female) )?(human|elven|dwarven|gnomish|orcish) "
                 r"(" + "|".join(_ROLES) + r")\b")
_FEMALE_ROLES = {"Cavewoman", "Priestess", "Valkyrie"}
_RE_CUT = re.compile(r"You are an? (lawful|neutral|chaotic) (?:(male|female) )?(human|elven|dwarven|gnomish|orcish)")
_RE_TITLE = re.compile(r"Agent the (\w+)")
# Xp 1 rank titles (role.c)
_TITLES = {"Digger": "Archeologist", "Plunderer": "Barbarian", "Plunderess": "Barbarian",
           "Troglodyte": "Caveman", "Rhizotomist": "Healer", "Gallant": "Knight", "Candidate": "Monk",
           "Aspirant": "Priest", "Tenderfoot": "Ranger", "Footpad": "Rogue", "Hatamoto": "Samurai",
           "Rambler": "Tourist", "Stripling": "Valkyrie", "Evoker": "Wizard"}


def _identity(observation):
    texts = []
    for key in ("message", "tty_chars"):
        try:
            texts.append(bytes(observation[key]).decode("latin-1", "replace"))
        except Exception:  # noqa: BLE001
            pass
    text = " ".join(texts)
    m = _RE.search(text)
    if m is not None:
        align, gender, race, role = m.groups()
    else:
        # an 80-column welcome line cuts the role off ("... neutral female gnomish"): take alignment, gender
        # and race from it and the role from the status line's Xp 1 rank title ("Agent the Digger")
        m = _RE_CUT.search(text)
        t = _RE_TITLE.search(text)
        if m is None or t is None or t.group(1) not in _TITLES:
            return None
        align, gender, race = m.groups()
        role = _TITLES[t.group(1)]
    gender = "fem" if gender == "female" or role in _FEMALE_ROLES else "mal"
    return f"{_ROLES[role]}-{_RACES[race]}-{_ALIGNS[align]}-{gender}"


class Bot:
    def __init__(self) -> None:
        self._drivers = {}
        self._driver = None

    def reset(self, initial_observation):
        ident = _identity(initial_observation)
        pkg = CHOICE.get(ident)
        if pkg is None and ident is not None:
            pkg = CHOICE.get(ident[:-3] + ("mal" if ident.endswith("fem") else "fem"))
        pkg = pkg or DEFAULT
        if pkg not in self._drivers:
            self._drivers[pkg] = importlib.import_module("adapter_" + pkg).AutoAscendDriver()
        self._driver = self._drivers[pkg]
        self._driver.reset(initial_observation)

    def act(self, observation):
        return self._driver.act(observation)

    def close(self):
        for driver in self._drivers.values():
            driver.close()


def make_agent():
    return Bot()
