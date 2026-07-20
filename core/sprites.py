"""Sprite path mappings for the map renderer."""

from pygamelogic import Potion, Weapon, Armor
# core/sprites.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(BASE_DIR, 'assets', 'sprites')

SPRITE_MAP = {
    '#': os.path.join(SPRITES_DIR, 'tile_wall.png'),
    '.': os.path.join(SPRITES_DIR, 'tile_floor.png'),
    '+': os.path.join(SPRITES_DIR, 'tile_door.png'),
    'O': os.path.join(SPRITES_DIR, 'tile_o2.png'),
    'P': os.path.join(SPRITES_DIR, 'tile_power.png'),
    'X': os.path.join(SPRITES_DIR, 'tile_pod.png'),
}
PLAYER_SPRITE = os.path.join(SPRITES_DIR, 'player.png')

ITEM_SPRITE_BY_TYPE = {
    'potion': os.path.join(SPRITES_DIR, 'item_potion.png'),
    'weapon': os.path.join(SPRITES_DIR, 'item_weapon.png'),
    'armor': os.path.join(SPRITES_DIR, 'item_armor.png'),
    'key': os.path.join(SPRITES_DIR, 'item_key.png'),
}
ENEMY_SPRITE_BY_NAME = {
    'Rogue Drone': os.path.join(SPRITES_DIR, 'enemy_drone.png'),
    'Mutant Rat': os.path.join(SPRITES_DIR, 'enemy_rat.png'),
    'Alien Creature': os.path.join(SPRITES_DIR, 'enemy_alien.png'),
    'Sentry Turret': os.path.join(SPRITES_DIR, 'enemy_turret.png'),
    'Rogue AI Drone': os.path.join(SPRITES_DIR, 'enemy_drone.png'),
    'Void Wraith': os.path.join(SPRITES_DIR, 'enemy_alien.png'),
}


def get_item_sprite(item):
    """Return the sprite path for an inventory item."""
    if isinstance(item, Potion):
        return ITEM_SPRITE_BY_TYPE['potion']
    elif isinstance(item, Weapon):
        return ITEM_SPRITE_BY_TYPE['weapon']
    elif isinstance(item, Armor):
        return ITEM_SPRITE_BY_TYPE['armor']
    elif getattr(item, 'item_type', None) == 'key':
        return ITEM_SPRITE_BY_TYPE['key']
    return ITEM_SPRITE_BY_TYPE['potion']  # fallback


def get_enemy_sprite(enemy):
    return ENEMY_SPRITE_BY_NAME.get(
        enemy.name, os.path.join(SPRITES_DIR, 'enemy_drone.png')
    )
