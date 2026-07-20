"""Hazard event definitions.

On mobile we cannot use pygamesense's run_event() because it calls
print()/input().  Instead we store descriptions and choice data here
and present them via Kivy popups.
"""


class HazardEvent:
    def __init__(self, description, choices):
        self.description = description
        self.choices = choices   # dict of key -> {text, damage}


HAZARD_EVENTS = [
    HazardEvent(
        "A hull breach hisses open nearby! Oxygen is venting fast.",
        {
            '1': {'text': 'Seal it with your multitool', 'damage': 0},
            '2': {'text': 'Run for the next room', 'damage': 15},
        }
    ),
    HazardEvent(
        "Power shutdown! The temperature moderator is failing and "
        "the station is slowly freezing.",
        {
            '1': {'text': 'Reroute auxiliary power to thermal regulators', 'damage': 0},
            '2': {'text': 'Equip heavy spacesuits and do a manual override', 'damage': 5},
        }
    ),
    HazardEvent(
        "A fire breaks out in the electrical bay! Sparks fly from "
        "the overloaded circuits and smoke fills the corridor.",
        {
            '1': {'text': 'Grab the extinguisher and fight the blaze', 'damage': 5},
            '2': {'text': 'Seal the bay and vent it to space', 'damage': 0},
        }
    ),
    HazardEvent(
        "You hear scratching in the vents above you. Something is "
        "moving through the ductwork, getting closer...",
        {
            '1': {'text': 'Quietly sneak past', 'damage': 0},
            '2': {'text': 'Bang on the vent to scare it off', 'damage': 10},
        }
    ),
    HazardEvent(
        "The airlock next to you malfunctions and begins cycling! "
        "The outer door is trying to open.",
        {
            '1': {'text': 'Override the airlock controls', 'damage': 0},
            '2': {'text': 'Brace yourself and hold on', 'damage': 20},
        }
    ),
    HazardEvent(
        "Warning! Radiation spike detected in this sector. Your "
        "suit's Geiger counter is clicking rapidly.",
        {
            '1': {'text': 'Sprint through the hot zone', 'damage': 10},
            '2': {'text': 'Find a lead-lined panel for shielding', 'damage': 0},
        }
    ),
]
