"""Procedural station map generator.

Produces a dict compatible with build_map_from_data():
    {'rows': [...], 'items': [...], 'enemies': [...], 'start_y': int, 'start_x': int}
"""
import random as _random_module

MAP_W = 60
MAP_H = 15

ITEM_POOL = [
    {'type': 'potion', 'name': 'Medkit', 'rarity': 'common', 'value': 10, 'heal_amount': 25},
    {'type': 'potion', 'name': 'Stim Pack', 'rarity': 'common', 'value': 5, 'heal_amount': 15},
    {'type': 'potion', 'name': 'Nano-Repair Kit', 'rarity': 'rare', 'value': 40, 'heal_amount': 50},
    {'type': 'weapon', 'name': 'Plasma Cutter', 'rarity': 'rare', 'value': 50, 'damage': 15},
    {'type': 'weapon', 'name': 'Ion Blaster', 'rarity': 'rare', 'value': 60, 'damage': 20},
    {'type': 'weapon', 'name': 'Emergency Wrench', 'rarity': 'common', 'value': 8, 'damage': 6},
    {'type': 'armor', 'name': 'Reinforced Vest', 'rarity': 'common', 'value': 20, 'defense': 5},
    {'type': 'armor', 'name': 'Shield Generator', 'rarity': 'rare', 'value': 55, 'defense': 10},
]

ENEMY_POOL = [
    {'name': 'Rogue Drone', 'health': 30, 'damage': 10},
    {'name': 'Mutant Rat', 'health': 20, 'damage': 8},
    {'name': 'Alien Creature', 'health': 40, 'damage': 12},
    {'name': 'Sentry Turret', 'health': 50, 'damage': 15},
    {'name': 'Rogue AI Drone', 'health': 35, 'damage': 11},
    {'name': 'Void Wraith', 'health': 60, 'damage': 18},
]


def _rooms_overlap(r1, r2):
    """Check if two rooms overlap (with 1-tile padding)."""
    return not (r1['x2'] + 1 < r2['x1'] or r2['x2'] + 1 < r1['x1'] or
                r1['y2'] + 1 < r2['y1'] or r2['y2'] + 1 < r1['y1'])


def generate_map(seed=None):
    """Generate a random station map.

    Returns a dict with keys: 'rows', 'items', 'enemies', 'start_y', 'start_x'.
    Using the same seed always produces the same map.
    """
    if seed is None:
        seed = _random_module.randint(0, 2**31 - 1)
    rng = _random_module.Random(seed)

    # Initialize grid with walls
    grid = [['#'] * MAP_W for _ in range(MAP_H)]

    # --- Place rooms ---
    target_rooms = rng.randint(6, 9)
    rooms = []

    for _ in range(target_rooms):
        placed = False
        for _attempt in range(200):
            w = rng.randint(4, 7)
            h = rng.randint(3, 5)
            x1 = rng.randint(1, MAP_W - w - 1)
            y1 = rng.randint(1, MAP_H - h - 1)
            candidate = {'x1': x1, 'y1': y1, 'x2': x1 + w - 1, 'y2': y1 + h - 1}

            if any(_rooms_overlap(candidate, r) for r in rooms):
                continue

            # Carve the room
            for ry in range(y1, y1 + h):
                for rx in range(x1, x1 + w):
                    grid[ry][rx] = '.'
            rooms.append(candidate)
            placed = True
            break
        # If not placed after 200 attempts, skip — fewer rooms is fine

    # Need at least 2 rooms for a playable map
    if len(rooms) < 2:
        # Fallback: force two small rooms
        grid[2][2] = grid[2][3] = grid[3][2] = grid[3][3] = '.'
        rooms.append({'x1': 2, 'y1': 2, 'x2': 3, 'y2': 3})
        grid[2][MAP_W - 4] = grid[2][MAP_W - 3] = grid[3][MAP_W - 4] = grid[3][MAP_W - 3] = '.'
        rooms.append({'x1': MAP_W - 4, 'y1': 2, 'x2': MAP_W - 3, 'y2': 3})

    # --- Connect rooms with L-shaped corridors ---
    # Track all corridor path tiles (not just newly carved) for door placement
    corridor_tiles = []

    for i in range(len(rooms) - 1):
        r1 = rooms[i]
        r2 = rooms[i + 1]
        cx1 = (r1['x1'] + r1['x2']) // 2
        cy1 = (r1['y1'] + r1['y2']) // 2
        cx2 = (r2['x1'] + r2['x2']) // 2
        cy2 = (r2['y1'] + r2['y2']) // 2

        this_corridor = []

        if rng.choice([True, False]):
            # Horizontal first, then vertical
            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                this_corridor.append((cy1, x))
                if grid[cy1][x] == '#':
                    grid[cy1][x] = '.'
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                this_corridor.append((y, cx2))
                if grid[y][cx2] == '#':
                    grid[y][cx2] = '.'
        else:
            # Vertical first, then horizontal
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                this_corridor.append((y, cx1))
                if grid[y][cx1] == '#':
                    grid[y][cx1] = '.'
            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                this_corridor.append((cy2, x))
                if grid[cy2][x] == '#':
                    grid[cy2][x] = '.'

        corridor_tiles.append(this_corridor)

    # --- Start and escape pod ---
    start_room = rooms[0]
    start_y = (start_room['y1'] + start_room['y2']) // 2
    start_x = (start_room['x1'] + start_room['x2']) // 2

    last_room = rooms[-1]
    pod_y = (last_room['y1'] + last_room['y2']) // 2
    pod_x = (last_room['x1'] + last_room['x2']) // 2
    grid[pod_y][pod_x] = 'X'

    # --- Locked door ---
    # Build set of all room interior tiles to avoid placing door inside a room
    room_tiles = set()
    for room in rooms:
        for ry in range(room['y1'], room['y2'] + 1):
            for rx in range(room['x1'], room['x2'] + 1):
                room_tiles.add((ry, rx))

    mid = len(rooms) // 2
    if mid < len(corridor_tiles):
        # Filter to corridor-only tiles (not inside rooms) on border rows
        corridor = [t for t in corridor_tiles[mid] if t not in room_tiles]
        if not corridor:
            # Fallback: use any corridor tile
            corridor = corridor_tiles[mid]
        if corridor:
            door_pos = rng.choice(corridor)
            grid[door_pos[0]][door_pos[1]] = '+'

    # --- O2 and Power tiles ---
    # Place in every other room (skip room 0 and last room), alternating O2/P
    o2_power_idx = 0
    for i in range(1, len(rooms) - 1):
        room = rooms[i]
        ry = (room['y1'] + room['y2']) // 2
        rx = (room['x1'] + room['x2']) // 2
        # Offset so it doesn't collide with items placed at center
        rx_off = min(rx + 1, room['x2'])
        if i % 2 == 1:
            tile = 'O' if o2_power_idx % 2 == 0 else 'P'
            grid[ry][rx_off] = tile
            o2_power_idx += 1

    # --- Keycard ---
    keycard_room_idx = max(0, mid - 1)
    keycard_room = rooms[keycard_room_idx]
    kc_y = (keycard_room['y1'] + keycard_room['y2']) // 2
    kc_x = (keycard_room['x1'] + keycard_room['x2']) // 2
    # If this is the start room center, offset
    if keycard_room_idx == 0:
        kc_x = min(kc_x + 1, keycard_room['x2'])

    items_list = [
        {'type': 'key', 'name': 'Keycard', 'rarity': 'common', 'value': 0,
         'y': kc_y, 'x': kc_x}
    ]

    # --- Place items ---
    # Rooms available for items: skip room 0 (start), last (pod), and keycard room
    used_rooms = {0, len(rooms) - 1, keycard_room_idx}
    available_rooms = [i for i in range(len(rooms)) if i not in used_rooms]

    num_items = rng.randint(5, 7)
    selected_items = rng.sample(ITEM_POOL, min(num_items, len(ITEM_POOL)))
    rng.shuffle(available_rooms)

    for idx, item_template in enumerate(selected_items):
        if idx >= len(available_rooms):
            break
        room = rooms[available_rooms[idx]]
        iy = (room['y1'] + room['y2']) // 2
        ix = (room['x1'] + room['x2']) // 2
        entry = dict(item_template)
        entry['y'] = iy
        entry['x'] = ix
        items_list.append(entry)

    # --- Place enemies ---
    enemy_available = [i for i in range(len(rooms)) if i not in {0, len(rooms) - 1}]
    rng.shuffle(enemy_available)

    num_enemies = rng.randint(4, 6)
    selected_enemies = rng.choices(ENEMY_POOL, k=num_enemies)

    enemies_list = []
    for idx, enemy_template in enumerate(selected_enemies):
        if idx >= len(enemy_available):
            break
        room = rooms[enemy_available[idx]]
        ey = room['y1'] + 1 if room['y1'] + 1 <= room['y2'] else room['y1']
        ex = room['x1'] + 1 if room['x1'] + 1 <= room['x2'] else room['x1']
        enemies_list.append({
            'name': enemy_template['name'],
            'health': enemy_template['health'],
            'damage': enemy_template['damage'],
            'y': ey,
            'x': ex,
        })

    # --- Build rows as strings ---
    rows = [''.join(row) for row in grid]

    return {
        'rows': rows,
        'items': items_list,
        'enemies': enemies_list,
        'start_y': start_y,
        'start_x': start_x,
    }
