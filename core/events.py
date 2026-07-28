"""Hazard event definitions.

On mobile we cannot use pygamesense's run_event() because it calls
print()/input().  Instead we store descriptions and choice data here
and present them via Kivy popups.
"""

from pygamelogic import Potion, Weapon, Armor


class HazardEvent:
    def __init__(self, description, choices):
        self.description = description
        self.choices = choices   # dict of key -> {text, effects}


def _build_item(spec):
    """Construct a pygamelogic item from a dict spec.

    Mirrors the construction logic in core/map_loader.py's load_map().
    """
    t = spec['item_type']
    if t == 'potion':
        return Potion(spec['name'], spec['rarity'],
                      spec['value'], spec['heal_amount'])
    elif t == 'weapon':
        return Weapon(spec['name'], spec['rarity'],
                      spec['value'], spec['damage'])
    elif t == 'armor':
        return Armor(spec['name'], spec['rarity'],
                     spec['value'], spec['defense'])
    raise ValueError(f'Unknown item_type: {t}')


def apply_effects(gs, effects):
    """Apply an effects dict to the game state and return a message string."""
    parts = []

    if 'health' in effects:
        delta = effects['health']
        gs.health = max(0, min(100, gs.health + delta))   # was: gs.health += delta
        if delta < 0:
            parts.append(f'You took {-delta} damage!')
        elif delta > 0:
            parts.append(f'You recovered {delta} HP!')

    if 'oxygen' in effects:
        delta = effects['oxygen']
        gs.oxygen = max(0, min(100, gs.oxygen + delta))
        if delta < 0:
            parts.append(f'Lost {-delta} oxygen!')
        elif delta > 0:
            parts.append(f'Recovered {delta} oxygen!')

    if 'power' in effects:
        delta = effects['power']
        gs.power = max(0, min(100, gs.power + delta))
        if delta < 0:
            parts.append(f'Lost {-delta} power!')
        elif delta > 0:
            parts.append(f'Recovered {delta} power!')

    if 'item_gain' in effects:
        item = _build_item(effects['item_gain'])
        try:
            gs.inventory.add_item(item)
            parts.append(f'Found {item.name}!')
        except ValueError:
            parts.append(f'Found {item.name}, but your inventory is full!')

    if not parts:
        return 'You handled the hazard safely!'
    return ' '.join(parts)


HAZARD_EVENTS = [
    HazardEvent(
        "A hull breach hisses open nearby! Oxygen is venting fast.",
        {
            '1': {'text': 'Seal it with your multitool', 'effects': {'health': 0}},
            '2': {'text': 'Run for the next room', 'effects': {'health': -15}},
            '3': {'text': 'Manually hold the seal shut', 'effects': {'oxygen': -20}},
        }
    ),
    HazardEvent(
        "Power shutdown! The temperature moderator is failing and "
        "the station is slowly freezing.",
        {
            '1': {'text': 'Reroute auxiliary power to thermal regulators', 'effects': {'health': 0}},
            '2': {'text': 'Equip heavy spacesuits and do a manual override', 'effects': {'health': -5}},
            '3': {'text': 'Let it fail and bundle up in emergency blankets', 'effects': {'power': -15}},
        }
    ),
    HazardEvent(
        "A fire breaks out in the electrical bay! Sparks fly from "
        "the overloaded circuits and smoke fills the corridor.",
        {
            '1': {'text': 'Grab the extinguisher and fight the blaze', 'effects': {'health': -5}},
            '2': {'text': 'Seal the bay and vent it to space', 'effects': {'health': 0}},
            '3': {'text': 'Salvage melted components before sealing it', 'effects': {'health': -5, 'item_gain': {'item_type': 'weapon', 'name': 'Salvaged Circuit Blade', 'rarity': 'common', 'value': 8, 'damage': 6}}},
        }
    ),
    HazardEvent(
        "You hear scratching in the vents above you. Something is "
        "moving through the ductwork, getting closer...",
        {
            '1': {'text': 'Quietly sneak past', 'effects': {'health': 0}},
            '2': {'text': 'Bang on the vent to scare it off', 'effects': {'health': -10}},
            '3': {'text': 'Peek inside the vent', 'effects': {'health': -5, 'item_gain': {'item_type': 'potion', 'name': 'Ration Bar', 'rarity': 'common', 'value': 5, 'heal_amount': 10}}},
        }
    ),
    HazardEvent(
        "The airlock next to you malfunctions and begins cycling! "
        "The outer door is trying to open.",
        {
            '1': {'text': 'Override the airlock controls', 'effects': {'health': 0}},
            '2': {'text': 'Brace yourself and hold on', 'effects': {'health': -20}},
            '3': {'text': 'Grab the emergency oxygen mask nearby', 'effects': {'oxygen': -15}},
        }
    ),
    HazardEvent(
        "Warning! Radiation spike detected in this sector. Your "
        "suit's Geiger counter is clicking rapidly.",
        {
            '1': {'text': 'Sprint through the hot zone', 'effects': {'health': -10}},
            '2': {'text': 'Find a lead-lined panel for shielding', 'effects': {'health': 0}},
            '3': {'text': 'Use your scanner to find a safer path', 'effects': {'power': -10}},
        }
    ),
]
