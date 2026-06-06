# -*- coding: utf-8 -*-

import json

from .settings import SAVE_FILE


def load_save_data():
    """Betölti a rekordokat a save_data.json fájlból."""
    default_data = {"best_goals": 0, "best_accuracy": 0}

    if not SAVE_FILE.exists():
        return default_data

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return default_data

    return {
        "best_goals": int(data.get("best_goals", 0)),
        "best_accuracy": int(data.get("best_accuracy", 0)),
    }


def save_high_score(high_score):
    """Elmenti a legjobb eredményt és pontosságot."""
    try:
        with SAVE_FILE.open("w", encoding="utf-8") as file:
            json.dump(high_score, file, ensure_ascii=False, indent=2)
    except OSError:
        # Ha valamiért nem sikerül menteni, a játék akkor is fusson tovább.
        pass
