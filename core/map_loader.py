import json
from pygamelogic import Potion, Weapon, Armor
from core.game_state import Enemy


class KeyItem:
    """Simple key item (pygamelogic has no Key class).

    Implements the attributes pygamelogic's InventorySystem expects:
    stackable, quantity, max_quantity.
    """
    def __init__(self, name, rarity='common', value=0):
        self.name = name
        self.rarity = rarity
        self.value = value
        self.item_type = 'key'
        self.stackable = False
        self.quantity = 1
        self.max_quantity = 1

    def __str__(self):
        return self.name


def load_map(filepath):
    """Load map JSON and return rows, active_items dict, active_enemies dict."""
    with open(filepath, 'r') as f:
        game_map = json.load(f)

    rows = game_map['rows']

    active_items = {}
    for entry in game_map['items']:
        position = (entry['y'], entry['x'])
        if entry['type'] == 'potion':
            active_items[position] = Potion(
                entry['name'], entry['rarity'],
                entry['value'], entry['heal_amount']
            )
        elif entry['type'] == 'weapon':
            active_items[position] = Weapon(
                entry['name'], entry['rarity'],
                entry['value'], entry['damage']
            )
        elif entry['type'] == 'armor':
            active_items[position] = Armor(
                entry['name'], entry['rarity'],
                entry['value'], entry['defense']
            )
        elif entry['type'] == 'key':
            active_items[position] = KeyItem(
                entry['name'], entry.get('rarity', 'common'),
                entry.get('value', 0)
            )

    active_enemies = {}
    for entry in game_map['enemies']:
        pos = (entry['y'], entry['x'])
        active_enemies[pos] = Enemy(
            entry['name'], entry['health'], entry['damage']
        )

    return rows, active_items, active_enemies
