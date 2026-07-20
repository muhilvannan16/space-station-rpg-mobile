from pygamelogic import Weapon, Armor


def get_weapon_damage(inventory):
    """Find the best weapon damage from inventory, default 5."""
    base = 5
    best = base
    for item in inventory.get_items():
        if isinstance(item, Weapon):
            best = max(best, item.damage)
    return best


def get_armor_defense(inventory):
    """Find the best armor defense from inventory, default 0."""
    best = 0
    for item in inventory.get_items():
        if isinstance(item, Armor):
            best = max(best, item.defense)
    return best


def calc_damage(raw_damage, defense):
    """Calculate actual damage after armor, minimum 1."""
    return max(1, raw_damage - defense)
