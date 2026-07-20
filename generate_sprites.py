"""Run once to generate placeholder 128x128 sprite PNGs.

Usage:
    pip install Pillow
    python generate_sprites.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), 'assets', 'sprites')
os.makedirs(OUT, exist_ok=True)

SIZE = (128, 128)

SPRITES = {
    'tile_wall':    {'bg': (40, 60, 40),    'label': '#',  'fg': (100, 180, 100)},
    'tile_floor':   {'bg': (50, 50, 50),    'label': '.',  'fg': (120, 120, 120)},
    'tile_door':    {'bg': (100, 30, 100),  'label': '+',  'fg': (220, 80, 220)},
    'tile_o2':      {'bg': (20, 40, 80),    'label': 'O2', 'fg': (80, 140, 255)},
    'tile_power':   {'bg': (80, 70, 10),    'label': 'P',  'fg': (255, 220, 50)},
    'tile_pod':     {'bg': (60, 60, 80),    'label': 'X',  'fg': (255, 255, 255)},
    'player':       {'bg': (10, 60, 60),    'label': '@',  'fg': (0, 255, 255)},
    'item_potion':  {'bg': (20, 50, 20),    'label': '+',  'fg': (100, 255, 100)},
    'item_weapon':  {'bg': (50, 20, 10),    'label': '/',  'fg': (255, 150, 80)},
    'item_armor':   {'bg': (30, 30, 50),    'label': 'A',  'fg': (150, 150, 255)},
    'item_key':     {'bg': (60, 50, 10),    'label': 'K',  'fg': (255, 215, 0)},
    'enemy_drone':  {'bg': (50, 10, 10),    'label': 'D',  'fg': (255, 80, 80)},
    'enemy_rat':    {'bg': (40, 30, 10),    'label': 'R',  'fg': (200, 150, 80)},
    'enemy_alien':  {'bg': (10, 40, 10),    'label': 'A',  'fg': (80, 255, 80)},
    'enemy_turret': {'bg': (40, 40, 40),    'label': 'T',  'fg': (255, 100, 100)},
}


def _get_font(size=48):
    """Try system fonts, fall back to default."""
    paths = [
        'C:/Windows/Fonts/consola.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    font = _get_font()
    for name, info in SPRITES.items():
        img = Image.new('RGBA', SIZE, info['bg'] + (255,))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), info['label'], font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (SIZE[0] - tw) // 2
        ty = (SIZE[1] - th) // 2
        draw.text((tx, ty), info['label'], fill=info['fg'] + (255,), font=font)
        if name.startswith('tile_'):
            draw.rectangle([0, 0, SIZE[0] - 1, SIZE[1] - 1],
                           outline=info['fg'] + (200,), width=2)
        img.save(os.path.join(OUT, f'{name}.png'))
        print(f'  {name}.png')
    print(f'\nDone — {len(SPRITES)} sprites saved to {OUT}')


if __name__ == '__main__':
    main()
