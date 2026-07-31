import random
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

BOSS_REWARD_POOL = [
    {'item_gain': {'item_type': 'weapon', 'name': 'Salvaged Core Blade',
                   'rarity': 'rare', 'value': 45, 'damage': 14}},
    {'item_gain': {'item_type': 'potion', 'name': 'Advanced Nano-Repair Kit',
                   'rarity': 'rare', 'value': 40, 'heal_amount': 50}},
    {'oxygen': 40},
    {'power': 40},
]

def roll_boss_reward():
    """Pick a random reward for defeating a boss. Returns an effects dict
    compatible with core.events.apply_effects()."""
    return random.choice(BOSS_REWARD_POOL)

    
def get_boss_attacks(boss, defense):
    """Return a list of individual damage amounts the boss deals this turn,
    based on its current phase (attacks_per_turn and damage_mult)."""
    phase = boss.current_phase()
    per_hit_raw = boss.damage * phase.get('damage_mult', 1.0)
    per_hit = int(round(calc_damage(per_hit_raw, defense)))
    return [per_hit] * phase.get('attacks_per_turn', 1)
