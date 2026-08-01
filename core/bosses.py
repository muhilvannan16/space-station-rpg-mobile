"""Per-sector boss definitions."""

from core.game_state import Boss


def get_boss_for_sector(sector):
    """Return a fresh Boss instance for the given sector (1-4)."""
    if sector == 1:
        return Boss(
            'Corrupted Sentry Turret', 30, 7,
            phases=[
                {'threshold': 1.0, 'attacks_per_turn': 1, 'damage_mult': 1.0,
                 'message': None},
                {'threshold': 0.5, 'attacks_per_turn': 2, 'damage_mult': 1.2,
                 'message': 'Its targeting systems overclock — it fires twice as fast!'},
            ],
        )
    if sector == 2:
        return Boss(
            'Corrupted Rogue AI Drone', 35, 7,
            phases=[
                {'threshold': 1.0, 'attacks_per_turn': 1, 'damage_mult': 1.0,
                 'message': None},
                {'threshold': 0.5, 'attacks_per_turn': 2, 'damage_mult': 1.2,
                 'message': 'Its circuits surge — targeting splits into twin beams!'},
            ],
        )
    if sector == 3:
        return Boss(
            'Xenomorph Broodmother', 40, 6,
            phases=[
                {'threshold': 1.0, 'attacks_per_turn': 1, 'damage_mult': 1.0,
                 'message': None},
                {'threshold': 0.5, 'attacks_per_turn': 2, 'damage_mult': 1.3,
                 'message': 'It screeches and splits its assault — claws lash from both sides!'},
            ],
        )
    # sector 4 (final boss) — three phases
    return Boss(
        'Station Core AI', 35, 6,
        phases=[
            {'threshold': 1.0, 'attacks_per_turn': 1, 'damage_mult': 1.0,
             'message': None},
            {'threshold': 0.6, 'attacks_per_turn': 2, 'damage_mult': 1.2,
             'message': 'The Core re-routes power — defense turrets spin online!'},
            {'threshold': 0.3, 'attacks_per_turn': 3, 'damage_mult': 1.4,
             'message': 'CRITICAL ALERT: Core activates all weapon arrays!'},
        ],
    )
