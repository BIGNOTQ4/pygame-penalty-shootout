# -*- coding: utf-8 -*-

import json
import sys
from pathlib import Path


DEFAULT_SAVE_DATA = {"best_goals": 0, "best_accuracy": 0}


def get_save_file_path():
    """Visszaadja, hova kerüljön a save_data.json.

    Normál Python futásnál a projekt gyökerébe mentünk.
    PyInstaller .exe esetén az exe fájl mappájába mentünk, hogy a rekord
    ugyanott legyen, ahol a felhasználó az alkalmazást futtatja.
    """
    if getattr(sys, "frozen", False):
        exe_folder = Path(sys.executable).resolve().parent
        return exe_folder / "save_data.json"

    project_root = Path(__file__).resolve().parent.parent
    return project_root / "save_data.json"


def create_default_save_file(save_file):
    """Létrehozza az alap mentési fájlt, ha még nem létezik."""
    try:
        with save_file.open("w", encoding="utf-8") as file:
            json.dump(DEFAULT_SAVE_DATA, file, ensure_ascii=False, indent=2)
    except OSError:
        # Ha nem sikerül létrehozni, a játék ettől még fusson tovább.
        pass


def load_save_data():
    """Betölti a rekordokat a save_data.json fájlból."""
    save_file = get_save_file_path()

    if not save_file.exists():
        create_default_save_file(save_file)
        return DEFAULT_SAVE_DATA.copy()

    try:
        with save_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SAVE_DATA.copy()

    return {
        "best_goals": int(data.get("best_goals", 0)),
        "best_accuracy": int(data.get("best_accuracy", 0)),
    }


def save_high_score(high_score):
    """Elmenti a legjobb eredményt és pontosságot."""
    save_file = get_save_file_path()

    try:
        with save_file.open("w", encoding="utf-8") as file:
            json.dump(high_score, file, ensure_ascii=False, indent=2)
    except OSError:
        # Ha valamiért nem sikerül menteni, a játék akkor is fusson tovább.
        pass
