"""Sound effect loading and playback.

Mirrors the path-resolution pattern in core/sprites.py — builds absolute
paths so sounds load reliably regardless of the working directory.
"""

import os
from kivy.core.audio import SoundLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, 'assets', 'sounds')

SOUND_FILES = {
    'pickup':       'pickup.ogg',
    'hazard':       'hazard.ogg',
    'attack':       'attack.ogg',
    'hit':          'hit.ogg',
    'door_locked':  'door_locked.ogg',
    'refill_o2':    'refill_o2.ogg',
    'refill_power': 'refill_power.ogg',
    'win':          'win.ogg',
    'lose':         'lose.ogg',
}

# Load all sounds at import time; missing files get a warning, not a crash.
SOUND_MAP = {}
for _name, _filename in SOUND_FILES.items():
    _path = os.path.join(SOUNDS_DIR, _filename)
    _sound = SoundLoader.load(_path)
    if _sound is not None:
        SOUND_MAP[_name] = _sound
    else:
        print(f'[sounds] WARNING: could not load {_path}')


def play_sound(name):
    """Play a named sound effect. Does nothing if the sound isn't loaded."""
    sound = SOUND_MAP.get(name)
    if sound is not None:
        sound.play()
