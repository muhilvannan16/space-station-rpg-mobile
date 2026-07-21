import os
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
        app.init_map()
        self.manager.current = 'game'

    def continue_game(self):
        app = self.manager.app
        app.game_state.reset()
        app.init_map()
        app.game_state.load_game()
        self.manager.current = 'game'

    def start_tutorial(self):
        tut = self.manager.get_screen('tutorial')
        tut._gs = None  # force fresh tutorial state
        self.manager.current = 'tutorial'
