import random
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from pygamelogic import Potion, Weapon, Armor

from core.combat import get_weapon_damage, get_armor_defense
from core.events import HAZARD_EVENTS
from core.sprites import (
    SPRITE_MAP, PLAYER_SPRITE, ITEM_SPRITE_BY_TYPE, ENEMY_SPRITE_BY_NAME,
    get_item_sprite, get_enemy_sprite,
)
from core.map_loader import KeyItem
from core.camera import compute_camera
from core.sounds import play_sound

# Viewport size (cells visible on screen)
VIEW_W = 9
VIEW_H = 7


class MapGrid(GridLayout):
    """Renders a fixed-size viewport window of the station map."""

    def __init__(self, view_w, view_h, **kwargs):
        super().__init__(**kwargs)
        self.cols = view_w
        self.view_w = view_w
        self.view_h = view_h
        self.tile_widgets = {}
        self.size_hint = (1, 1)

        for vy in range(view_h):
            for vx in range(view_w):
                img = Image(
                    source=SPRITE_MAP['.'],
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint=(1, 1),
                )
                self.add_widget(img)
                self.tile_widgets[(vy, vx)] = img

    def update_tile(self, vy, vx, sprite_path):
        """Set the sprite at viewport-relative position (vy, vx)."""
        key = (vy, vx)
        if key in self.tile_widgets:
            self.tile_widgets[key].source = sprite_path
            self.tile_widgets[key].reload()


class InventoryPopup(Popup):
    """Popup declared in game.kv; item rows are built in Python."""
    pass


class GameScreen(Screen):
    oxygen = NumericProperty(100)
    power = NumericProperty(100)
    health = NumericProperty(100)
    message = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.map_grid = None
        self._gs = None  # game state ref, set on_enter

    def on_enter(self, *args):
        self._gs = self.manager.app.game_state
        # Sync Kivy properties from game state
        self.oxygen = self._gs.oxygen
        self.power = self._gs.power
        self.health = self._gs.health
        self.message = self._gs.message
        self.build_map()

    def build_map(self):
        container = self.ids.get('map_container')
        if container is None:
            return
        container.clear_widgets()

        self.map_grid = MapGrid(VIEW_W, VIEW_H)
        container.add_widget(self.map_grid)

        self._redraw_viewport()

    def _redraw_viewport(self):
        """Recompute the camera and repaint every cell in the viewport."""
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
                # World coordinates for this viewport cell
                wy = cam_y + vy
                wx = cam_x + vx

                # Determine what sprite to show
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

    # --- Movement (called by D-pad buttons) ---
    def move_player(self, dx, dy):
        gs = self._gs
        if gs is None:
            return

        new_y = gs.player_y + dy
        new_x = gs.player_x + dx

        # Boundary clamping
        new_x = max(0, min(new_x, len(gs.rows[0]) - 1))
        new_y = max(0, min(new_y, len(gs.rows) - 1))

        # Enemy collision -> combat screen
        if (new_y, new_x) in gs.active_enemies:
            enemy = gs.active_enemies[(new_y, new_x)]
            combat = self.manager.get_screen('combat')
            combat.setup(enemy, (new_y, new_x))
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
                play_sound('door_locked')
                self._sync_hud()
                return

        # Wall collision
        if gs.rows[new_y][new_x] == '#':
            return

        # Move player in game state (no per-tile widget updates needed —
        # _redraw_viewport repaints the whole window)
        gs.player_y, gs.player_x = new_y, new_x

        # Deplete resources
        gs.oxygen -= 1
        gs.step_count += 1
        if gs.step_count % 3 == 0:
            gs.power -= 1

        # Tile effects (may end the game)
        if self._check_tile_effects():
            return

        # Item pickup
        self._check_item_pickup()

        # Random hazard (10% chance)
        if random.randint(1, 10) == 1:
            self._trigger_hazard()

        # Redraw the viewport and sync HUD
        self._redraw_viewport()
        self._sync_hud()

    def _check_tile_effects(self):
        """Check current tile for effects. Returns True if the game ended."""
        gs = self._gs
        tile = gs.rows[gs.player_y][gs.player_x]
        if tile == 'O':
            gs.oxygen = min(100, gs.oxygen + 30)
            gs.message = 'Oxygen refilled!'
            play_sound('refill_o2')
        elif tile == 'P':
            gs.power = min(100, gs.power + 20)
            gs.message = 'Power restored!'
            play_sound('refill_power')
        elif tile == 'X':
            gs.message = 'You reached the escape pod!'
            play_sound('win')
            self._sync_hud()
            end = self.manager.get_screen('end')
            end.result = 'YOU WIN: You escaped the station!'
            self.manager.current = 'end'
            return True

        if gs.oxygen <= 0:
            gs.message = 'You suffocated!'
            play_sound('lose')
            self._sync_hud()
            end = self.manager.get_screen('end')
            end.result = 'GAME OVER: You suffocated.'
            self.manager.current = 'end'
            return True

        return False

    def _check_item_pickup(self):
        gs = self._gs
        pos = (gs.player_y, gs.player_x)
        if pos in gs.active_items:
            item = gs.active_items[pos]
            gs.inventory.add_item(item)
            gs.message = f'Picked up {item.name}!'
            play_sound('pickup')
            del gs.active_items[pos]
            gs.picked_up_items.append([pos[0], pos[1]])

    def _trigger_hazard(self):
        event = random.choice(HAZARD_EVENTS)
        play_sound('hazard')
        evt_screen = self.manager.get_screen('event')
        evt_screen.setup(event)
        self.manager.current = 'event'

    def _sync_hud(self):
        gs = self._gs
        self.oxygen = gs.oxygen
        self.power = gs.power
        self.health = gs.health
        self.message = gs.message

    def open_inventory(self):
        gs = self._gs
        if gs is None:
            return
        popup = InventoryPopup()
        self._populate_inventory(popup)
        popup.open()

    def _populate_inventory(self, popup):
        item_list = popup.ids.get('item_list')
        if item_list is None:
            return
        item_list.clear_widgets()

        items = gs_items = self._gs.inventory.get_items()
        if not items:
            lbl = Label(
                text='Inventory is empty.',
                font_size='14sp',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=40,
            )
            item_list.add_widget(lbl)
            return

        for item in items:
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=50,
                spacing=10,
            )

            # Build description based on item type
            if isinstance(item, Potion):
                desc = f'{item.name}  —  Potion, heals: {item.heal_amount}'
            elif isinstance(item, Weapon):
                desc = f'{item.name}  —  Weapon, damage: {item.damage}'
            elif isinstance(item, Armor):
                desc = f'{item.name}  —  Armor, defense: {item.defense}'
            else:
                desc = f'{item.name}  —  Key item'

            lbl = Label(
                text=desc,
                font_size='13sp',
                color=(1, 1, 1, 1),
                halign='left',
                valign='middle',
                text_size=(None, None),
            )
            lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
            row.add_widget(lbl)

            if isinstance(item, Potion):
                btn = Button(
                    text='Use',
                    font_size='13sp',
                    size_hint_x=0.25,
                    bold=True,
                )
                btn.bind(on_press=lambda inst, p=item, pop=popup: self.use_potion(p, pop))
                row.add_widget(btn)

            item_list.add_widget(row)

    def use_potion(self, potion, popup):
        gs = self._gs
        try:
            gs.inventory.use_item(potion, gs)
            gs.message = f'Used {potion.name}! Healed up.'
        except ValueError as e:
            gs.message = str(e)

        gs.oxygen -= 1
        gs.step_count += 1
        if gs.step_count % 3 == 0:
            gs.power -= 1

        if gs.oxygen <= 0:
            gs.message = 'You suffocated!'
            play_sound('lose')
            self._sync_hud()
            popup.dismiss()
            end = self.manager.get_screen('end')
            end.result = 'GAME OVER: You suffocated.'
            self.manager.current = 'end'
            return

        if random.randint(1, 10) == 1:
            popup.dismiss()
            self._trigger_hazard()
            return

        self._sync_hud()
        self._populate_inventory(popup)

    def do_save(self):
        gs = self._gs
        gs.save_game()
        gs.message = 'Game saved!'
        self._sync_hud()
