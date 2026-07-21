from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

from core.game_state import GameState
from core.map_loader import load_map, KeyItem
from core.sprites import (
    SPRITE_MAP, PLAYER_SPRITE,
    get_item_sprite, get_enemy_sprite,
)
from core.camera import compute_camera
from core.sounds import play_sound
from screens.game_screen import MapGrid, VIEW_W, VIEW_H


# Each step has a type (event key) and instruction text shown to the player.
TUTORIAL_STEPS = [
    {
        'type': 'move',
        'instruction': 'Use the D-pad to move your character.',
    },
    {
        'type': 'pickup',
        'instruction': 'Walk onto the Medkit to pick it up.',
    },
    {
        'type': 'refill_o2',
        'instruction': 'Step on the O2 station (blue tile) to refill oxygen.',
    },
    {
        'type': 'refill_power',
        'instruction': 'Step on the Power station (yellow tile) to restore power.',
    },
    {
        'type': 'door_locked',
        'instruction': 'Try to open the door ahead. It\'s locked!',
    },
    {
        'type': 'pickup_key',
        'instruction': 'Find the Keycard in the alcove below.',
    },
    {
        'type': 'door_open',
        'instruction': 'Return to the door and open it with the Keycard.',
    },
    {
        'type': 'combat_win',
        'instruction': 'Defeat the Training Dummy!',
    },
    {
        'type': 'win',
        'instruction': 'Reach the Escape Pod to complete the tutorial!',
    },
]


class TutorialScreen(Screen):
    instruction = StringProperty('')
    message = StringProperty('')
    oxygen = NumericProperty(100)
    power = NumericProperty(100)
    health = NumericProperty(100)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gs = None
        self.map_grid = None
        self.current_step = 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_enter(self, *args):
        if self._gs is None:
            self._init_tutorial()
        else:
            # Returning from combat — only advance if the enemy was actually defeated
            self.build_map()
            if not self._gs.active_enemies:
                self._check_step('combat_win')

    def _init_tutorial(self):
        """Set up an isolated game state and load the tutorial map."""
        gs = GameState()
        gs.reset()
        gs.player_y = 1
        gs.player_x = 1
        rows, items, enemies = load_map('assets/maps/tutorial_map.json')
        gs.rows = rows
        gs.active_items = items
        gs.active_enemies = enemies
        self._gs = gs

        self.current_step = 0
        self.instruction = TUTORIAL_STEPS[0]['instruction']
        self.message = 'Welcome to the tutorial!'
        self._sync_hud()
        self.build_map()

    # ------------------------------------------------------------------
    # Map rendering (reuses MapGrid + camera from game_screen)
    # ------------------------------------------------------------------
    def build_map(self):
        container = self.ids.get('tut_map_container')
        if container is None:
            return
        container.clear_widgets()
        self.map_grid = MapGrid(VIEW_W, VIEW_H)
        container.add_widget(self.map_grid)
        self._redraw_viewport()

    def _redraw_viewport(self):
        gs = self._gs
        mg = self.map_grid
        if gs is None or mg is None:
            return

        map_h = len(gs.rows)
        map_w = len(gs.rows[0]) if map_h else 0
        cam_y, cam_x = compute_camera(
            gs.player_x, gs.player_y, map_w, map_h, VIEW_W, VIEW_H
        )

        for vy in range(VIEW_H):
            for vx in range(VIEW_W):
                wy = cam_y + vy
                wx = cam_x + vx
                world_pos = (wy, wx)

                if wy == gs.player_y and wx == gs.player_x:
                    sprite = PLAYER_SPRITE
                elif world_pos in gs.active_enemies:
                    sprite = get_enemy_sprite(gs.active_enemies[world_pos])
                elif world_pos in gs.active_items:
                    sprite = get_item_sprite(gs.active_items[world_pos])
                else:
                    char = gs.rows[wy][wx]
                    sprite = SPRITE_MAP.get(char, SPRITE_MAP['.'])

                mg.update_tile(vy, vx, sprite)

    # ------------------------------------------------------------------
    # Step tracking
    # ------------------------------------------------------------------
    def _check_step(self, event_type):
        """Advance the tutorial if *event_type* matches the current step."""
        if self.current_step >= len(TUTORIAL_STEPS):
            return
        if TUTORIAL_STEPS[self.current_step]['type'] != event_type:
            return

        self.current_step += 1
        if self.current_step < len(TUTORIAL_STEPS):
            self.instruction = TUTORIAL_STEPS[self.current_step]['instruction']
        else:
            # Tutorial complete
            self.instruction = 'Tutorial complete!'
            play_sound('win')
            end = self.manager.get_screen('end')
            end.result = "Tutorial Complete! You're ready for the real mission."
            Clock.schedule_once(lambda dt: setattr(
                self.manager, 'current', 'end'), 1.5)

    # ------------------------------------------------------------------
    # Movement (simplified — no O2/power depletion, no random hazards)
    # ------------------------------------------------------------------
    def move_player(self, dx, dy):
        gs = self._gs
        if gs is None:
            return

        new_y = gs.player_y + dy
        new_x = gs.player_x + dx

        # Boundary clamping
        new_x = max(0, min(new_x, len(gs.rows[0]) - 1))
        new_y = max(0, min(new_y, len(gs.rows) - 1))

        # Enemy collision → combat
        if (new_y, new_x) in gs.active_enemies:
            enemy = gs.active_enemies[(new_y, new_x)]
            combat = self.manager.get_screen('combat')
            combat.setup(enemy, (new_y, new_x),
                         game_state=self._gs, return_screen='tutorial')
            self.manager.current = 'combat'
            return

        # Locked door check
        if gs.rows[new_y][new_x] == '+':
            has_key = any(
                getattr(item, 'name', '') == 'Keycard'
                for item in gs.inventory.get_items()
            )
            if not has_key:
                gs.message = 'This door is locked. Find a keycard.'
                self.message = gs.message
                play_sound('door_locked')
                self._check_step('door_locked')
                return
            else:
                # Door opens with keycard
                self._check_step('door_open')

        # Wall collision
        if gs.rows[new_y][new_x] == '#':
            return

        # Move player
        gs.player_y, gs.player_x = new_y, new_x

        # First move completes the 'move' step
        self._check_step('move')

        # Tile effects
        if self._check_tile_effects():
            return

        # Item pickup
        self._check_item_pickup()

        # Redraw
        self._redraw_viewport()
        self._sync_hud()

    def _check_tile_effects(self):
        gs = self._gs
        tile = gs.rows[gs.player_y][gs.player_x]
        if tile == 'O':
            gs.oxygen = min(100, gs.oxygen + 30)
            gs.message = 'Oxygen refilled!'
            self.message = gs.message
            play_sound('refill_o2')
            self._check_step('refill_o2')
        elif tile == 'P':
            gs.power = min(100, gs.power + 20)
            gs.message = 'Power restored!'
            self.message = gs.message
            play_sound('refill_power')
            self._check_step('refill_power')
        elif tile == 'X':
            gs.message = 'You reached the escape pod!'
            self.message = gs.message
            self._check_step('win')
            return True
        return False

    def _check_item_pickup(self):
        gs = self._gs
        pos = (gs.player_y, gs.player_x)
        if pos in gs.active_items:
            item = gs.active_items[pos]
            gs.inventory.add_item(item)
            gs.message = f'Picked up {item.name}!'
            self.message = gs.message
            play_sound('pickup')
            del gs.active_items[pos]

            # Determine which step this satisfies
            if isinstance(item, KeyItem) or getattr(item, 'item_type', '') == 'key':
                self._check_step('pickup_key')
            else:
                self._check_step('pickup')

    def _sync_hud(self):
        gs = self._gs
        self.oxygen = gs.oxygen
        self.power = gs.power
        self.health = gs.health
        self.message = gs.message

    # ------------------------------------------------------------------
    # Skip / exit
    # ------------------------------------------------------------------
    def skip_tutorial(self):
        """Return to title screen, discarding tutorial state."""
        self._gs = None
        self.manager.current = 'title'
