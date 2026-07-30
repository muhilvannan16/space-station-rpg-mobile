from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from core.game_state import GameState


class TitleScreen(Screen):
    has_save = BooleanProperty(False)

    def on_enter(self, *args):
        self.has_save = GameState.has_save()

    def new_game(self):
        GameState.delete_save()
        app = self.manager.app
        app.game_state.reset()
        from core.map_generator import generate_map, sector_difficulty
        from core.map_loader import build_map_from_data
        params = sector_difficulty(1)
        map_data = generate_map(**params)
        rows, items, enemies = build_map_from_data(map_data)
        app.game_state.set_map(rows, items, enemies,
                               map_data['start_y'], map_data['start_x'])
        self.manager.current = 'game'

    def continue_game(self):
        app = self.manager.app
        app.game_state.reset()
        app.game_state.load_game()
        self.manager.current = 'game'

    def start_tutorial(self):
        tut = self.manager.get_screen('tutorial')
        tut._gs = None  # force fresh tutorial state
        self.manager.current = 'tutorial'
