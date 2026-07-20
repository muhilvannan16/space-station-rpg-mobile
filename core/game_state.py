import os
import json
from kivy.event import EventDispatcher
from kivy.properties import (
    NumericProperty, StringProperty, ListProperty, DictProperty
)
from kivy.utils import platform
from pygamelogic import InventorySystem, Potion, Weapon, Armor


class Enemy:
    def __init__(self, name, health, damage):
        self.name = name
        self.health = health
        self.damage = damage


class GameState(EventDispatcher):
    """Centralized game state shared across all screens."""
    player_y = NumericProperty(5)
    player_x = NumericProperty(10)
    oxygen = NumericProperty(100)
    power = NumericProperty(100)
    health = NumericProperty(100)
    step_count = NumericProperty(0)
    message = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inventory = InventorySystem(capacity=10)
        self.rows = []
        self.active_items = {}
        self.active_enemies = {}
        self.picked_up_items = []
        self.killed_enemies = []

    def reset(self):
        self.player_y = 5
        self.player_x = 10
        self.oxygen = 100
        self.power = 100
        self.health = 100
        self.step_count = 0
        self.message = ''
        self.inventory = InventorySystem(capacity=10)
        self.picked_up_items = []
        self.killed_enemies = []

    # --- Save / Load ---
    @staticmethod
    def get_save_path():
        if platform == 'android':
            from android.storage import app_storage_path
            return os.path.join(app_storage_path(), 'savegame.json')
        return os.path.join('save', 'savegame.json')

    def save_game(self):
        path = self.get_save_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            'player_y': self.player_y,
            'player_x': self.player_x,
            'oxygen': self.oxygen,
            'power': self.power,
            'step_count': self.step_count,
            'health': self.health,
            'picked_up_items': self.picked_up_items,
            'killed_enemies': self.killed_enemies,
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load_game(self):
        path = self.get_save_path()
        if not os.path.exists(path):
            return False
        with open(path, 'r') as f:
            data = json.load(f)
        self.player_y = data['player_y']
        self.player_x = data['player_x']
        self.oxygen = data['oxygen']
        self.power = data['power']
        self.step_count = data['step_count']
        self.health = data['health']
        # Remove already-picked-up items
        for pos in data.get('picked_up_items', []):
            key = (pos[0], pos[1])
            self.active_items.pop(key, None)
        # Remove already-killed enemies
        for pos in data.get('killed_enemies', []):
            key = (pos[0], pos[1])
            self.active_enemies.pop(key, None)
        self.picked_up_items = data.get('picked_up_items', [])
        self.killed_enemies = data.get('killed_enemies', [])
        return True

    @classmethod
    def has_save(cls):
        return os.path.exists(cls.get_save_path())

    @classmethod
    def delete_save(cls):
        path = cls.get_save_path()
        if os.path.exists(path):
            os.remove(path)
