import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.utils import platform

from core.game_state import GameState
from core.map_loader import load_map
from screens.title_screen import TitleScreen
from screens.game_screen import GameScreen
from screens.combat_screen import CombatScreen
from screens.event_screen import EventScreen, EndScreen

# Auto-generate placeholder sprites if missing
_sprite_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sprites')
if not os.path.isdir(_sprite_dir):
    try:
        from generate_sprites import main as _gen
        _gen()
    except Exception:
        pass

# Load the KV layout file
Builder.load_file('game.kv')


class SpaceStationApp(App):
    title = 'Space Station RPG'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = GameState()

    def build(self):
        sm = ScreenManager()
        sm.app = self  # back-reference so screens can reach app

        sm.add_widget(TitleScreen(name='title'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(CombatScreen(name='combat'))
        sm.add_widget(EventScreen(name='event'))
        sm.add_widget(EndScreen(name='end'))

        return sm

    def init_map(self):
        """Load map data into game_state. Called before entering game screen."""
        if platform == 'android':
            map_path = 'assets/maps/station.json'
        else:
            map_path = 'assets/maps/station.json'

        rows, items, enemies = load_map(map_path)
        self.game_state.rows = rows
        self.game_state.active_items = items
        self.game_state.active_enemies = enemies


if __name__ == '__main__':
    SpaceStationApp().run()
