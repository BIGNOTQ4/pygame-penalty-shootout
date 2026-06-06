# -*- coding: utf-8 -*-

import math
from array import array

import pygame


def make_tone(frequency, duration, volume=0.35, wave="sine"):
    """Egyszerű hangot készít fájl nélkül, csak Python kódból."""
    sample_rate = 44100
    sample_count = int(sample_rate * duration)
    samples = array("h")

    for index in range(sample_count):
        time = index / sample_rate
        fade = 1 - index / sample_count

        if wave == "square":
            value = 1 if math.sin(math.tau * frequency * time) > 0 else -1
        else:
            value = math.sin(math.tau * frequency * time)

        samples.append(int(value * volume * fade * 32767))

    return pygame.mixer.Sound(buffer=samples.tobytes())


def create_sounds():
    """Létrehozza a játék rövid hangjait. Hiba esetén csendben fut tovább."""
    try:
        return {
            "shoot": make_tone(180, 0.12, 0.35, "square"),
            "goal": make_tone(660, 0.35, 0.35),
            "save": make_tone(95, 0.22, 0.45, "square"),
            "miss": make_tone(240, 0.30, 0.25),
        }
    except pygame.error:
        return {}


def play_sound(sounds, name):
    """Biztonságos hanglejátszás: ha nincs hang, nem történik semmi."""
    sound = sounds.get(name)
    if sound:
        sound.play()
