from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty

from core.events import apply_effects


class EventScreen(Screen):
    description = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event = None

    def setup(self, event):
        self.event = event
        self.description = event.description

    def on_enter(self, *args):
        btn_box = self.ids.get('choice_buttons')
        if btn_box is None:
            return
        btn_box.clear_widgets()
        for key, choice in self.event.choices.items():
            btn = Button(
                text=choice['text'],
                size_hint_y=None,
                height=60,
                font_size='14sp',
            )
            effects = choice['effects']
            btn.bind(on_press=lambda inst, e=effects: self.choose(e))
            btn_box.add_widget(btn)

    def choose(self, effects):
        gs = self.manager.app.game_state
        gs.message = apply_effects(gs, effects)

        if gs.health <= 0:
            end = self.manager.get_screen('end')
            end.result = 'GAME OVER: You were killed.'
            self.manager.current = 'end'
        else:
            self.manager.current = 'game'


class EndScreen(Screen):
    result = StringProperty('Game Over')
