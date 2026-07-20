from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty


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
            damage = choice['damage']
            btn.bind(on_press=lambda inst, d=damage: self.choose(d))
            btn_box.add_widget(btn)

    def choose(self, damage):
        gs = self.manager.app.game_state
        gs.health -= damage
        if damage > 0:
            gs.message = f'You took {damage} damage from the hazard!'
        else:
            gs.message = 'You handled the hazard safely!'

        if gs.health <= 0:
            end = self.manager.get_screen('end')
            end.result = 'GAME OVER: You were killed.'
            self.manager.current = 'end'
        else:
            self.manager.current = 'game'


class EndScreen(Screen):
    result = StringProperty('Game Over')
