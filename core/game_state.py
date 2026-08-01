import os
import json
from kivy.event import EventDispatcher
from kivy.properties import (
    NumericProperty, StringProperty, ListProperty, DictProperty
)
from kivy.utils import platform
from pygamelogic import InventorySystem, Potion, Weapon, Armor


def _item_to_dict(item):
    """Serialize an inventory item to a JSON-safe dict."""
    if isinstance(item, Potion):
        return {'item_type': 'potion', 'name': item.name, 'rarity': item.rarity,
                'value': item.value, 'heal_amount': item.heal_amount,
                'quantity': item.quantity}
    if isinstance(item, Weapon):
        return {'item_type': 'weapon', 'name': item.name, 'rarity': item.rarity,
                'value': item.value, 'damage': item.damage}
    if isinstance(item, Armor):
        return {'item_type': 'armor', 'name': item.name, 'rarity': item.rarity,
                'value': item.value, 'defense': item.defense}
    from core.map_loader import KeyItem
    if isinstance(item, KeyItem):
        return {'item_type': 'key', 'name': item.name, 'rarity': item.rarity,
                'value': item.value}
    return None


def _map_item_to_dict(pos, item):
    """Serialize an inventory item with its map position.

    Renames 'item_type' to 'type' so the dict matches the format
    expected by build_map_from_data (same as station.json).
    """
    d = _item_to_dict(item)
    if d is not None:
        d['type'] = d.pop('item_type')
        d['y'], d['x'] = pos
    return d


def _item_from_dict(spec):
    """Reconstruct an inventory item from a serialized dict."""
    from core.map_loader import KeyItem
    t = spec['item_type']
    if t == 'potion':
        return Potion(spec['name'], spec['rarity'], spec['value'],
                      spec['heal_amount'], quantity=spec.get('quantity', 1))
    if t == 'weapon':
        return Weapon(spec['name'], spec['rarity'], spec['value'], spec['damage'])
    if t == 'armor':
        return Armor(spec['name'], spec['rarity'], spec['value'], spec['defense'])
    if t == 'key':
        return KeyItem(spec['name'], spec.get('rarity', 'common'), spec.get('value', 0))
    return None


class Enemy:
    def __init__(self, name, health, damage):
        self.name = name
        self.health = health
        self.damage = damage
        
class Boss(Enemy):
    """A multi-phase enemy. `phases` is a list of dicts, ordered from full
    health to lowest health, each with:
        'threshold': HP fraction (0-1) at or below which this phase begins
        'attacks_per_turn': how many times it attacks in a single turn
        'damage_mult': multiplier applied to self.damage for this phase
        'message': text shown once, the turn this phase begins (or None)
    Phase 0 must have threshold=1.0 (active from full health).
    """
    def __init__(self, name, health, damage, phases):
        super().__init__(name, health, damage)
        self.max_health = health
        self.phases = phases
        self.phase_index = 0

    def current_phase(self):
        return self.phases[self.phase_index]

    def check_phase_transition(self):
        """Recompute which phase should be active based on current HP.
        Returns the new phase dict if this call caused a transition,
        otherwise None."""
        hp_fraction = self.health / self.max_health if self.max_health else 0
        new_index = 0
        for i, phase in enumerate(self.phases):
            if hp_fraction <= phase['threshold']:
                new_index = i
        if new_index != self.phase_index:
            self.phase_index = new_index
            return self.phases[new_index]
        return None


class GameState(EventDispatcher):
    """Centralized game state shared across all screens."""
    TOTAL_SECTORS = 4

    player_y = NumericProperty(5)
    player_x = NumericProperty(10)
    oxygen = NumericProperty(100)
    power = NumericProperty(100)
    health = NumericProperty(100)
    step_count = NumericProperty(0)
    current_sector = NumericProperty(1)
    message = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inventory = InventorySystem(capacity=10)
        self.rows = []
        self.active_items = {}
        self.active_enemies = {}
        self.template_items = {}
        self.template_enemies = {}
        self.boss_defeated = False
        self.current_boss = None
        self.picked_up_items = []
        self.killed_enemies = []

    def reset(self):
        self.player_y = 5
        self.player_x = 10
        self.oxygen = 100
        self.power = 100
        self.health = 100
        self.step_count = 0
        self.current_sector = 1
        self.message = ''
        self.inventory = InventorySystem(capacity=10)
        self.template_items = {}
        self.template_enemies = {}
        self.picked_up_items = []
        self.killed_enemies = []

    def set_map(self, rows, items, enemies, start_y, start_x):
        """Apply a generated or loaded map to the game state."""
        self.rows = rows
        self.template_items = dict(items)
        self.template_enemies = dict(enemies)
        self.active_items = dict(items)
        self.active_enemies = dict(enemies)
        self.player_y = start_y
        self.player_x = start_x
        self.boss_defeated = False
        self.current_boss = None
        self.picked_up_items = []
        self.killed_enemies = []

    def advance_sector(self):
        """Move to the next sector: fresh map, refill life support, keep HP/inventory."""
        from core.map_generator import generate_map, sector_difficulty
        from core.map_loader import build_map_from_data
        self.current_sector += 1
        params = sector_difficulty(self.current_sector)
        map_data = generate_map(**params)
        rows, items, enemies = build_map_from_data(map_data)
        self.set_map(rows, items, enemies, map_data['start_y'], map_data['start_x'])
        self.oxygen = 100
        self.power = 100
        self.message = f'Sector {self.current_sector} reached — life support restored!'

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
            'current_sector': self.current_sector,
            'health': self.health,
            'boss_defeated': self.boss_defeated,
            'picked_up_items': self.picked_up_items,
            'killed_enemies': self.killed_enemies,
            'inventory': [d for d in (_item_to_dict(i) for i in self.inventory.get_items()) if d is not None],
            'map': {
                'rows': self.rows,
                'items': [d for d in (_map_item_to_dict(pos, item) for pos, item in self.template_items.items()) if d is not None],
                'enemies': [{'name': e.name, 'health': e.health, 'damage': e.damage, 'y': pos[0], 'x': pos[1]} for pos, e in self.template_enemies.items()],
            },
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
        self.current_sector = data.get('current_sector', 1)
        self.health = data['health']
        self.boss_defeated = data.get('boss_defeated', False)
        # Restore inventory
        self.inventory = InventorySystem(capacity=10)
        for spec in data.get('inventory', []):
            item = _item_from_dict(spec)
            if item is not None:
                self.inventory.add_item(item)
        # Restore map from save data
        from core.map_loader import build_map_from_data
        map_data = data.get('map')
        if map_data:
            rows, items, enemies = build_map_from_data(map_data)
            self.rows = rows
            self.template_items = dict(items)
            self.template_enemies = dict(enemies)
            self.active_items = dict(items)
            self.active_enemies = dict(enemies)
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

    def heal_health(self, amount):
        self.health = min(100, self.health + amount)

    @classmethod
    def has_save(cls):
        return os.path.exists(cls.get_save_path())

    @classmethod
    def delete_save(cls):
        path = cls.get_save_path()
        if os.path.exists(path):
            os.remove(path)
