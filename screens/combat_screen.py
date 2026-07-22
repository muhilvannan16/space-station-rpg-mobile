from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

from core.combat import get_weapon_damage, get_armor_defense, calc_damage
from core.sounds import play_sound


class CombatScreen(Screen):
    enemy_name = StringProperty('')
    enemy_hp = NumericProperty(0)
    player_hp = NumericProperty(0)
    weapon_damage = NumericProperty(5)
    defense = NumericProperty(0)
    message = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enemy = None
        self.enemy_pos = None
        self._combat_over = False

    def setup(self, enemy, pos, game_state=None, return_screen='game'):
        self.enemy = enemy
        self.enemy_pos = pos
        self.enemy_killed = False
        self._combat_over = False
        self._gs = game_state or self.manager.app.game_state
        self._return_screen = return_screen

    def on_enter(self, *args):
        gs = self._gs
        self.enemy_name = self.enemy.name
        self.enemy_hp = max(0, self.enemy.health)
        self.player_hp = max(0, gs.health)
        self.weapon_damage = get_weapon_damage(gs.inventory)
        self.defense = get_armor_defense(gs.inventory)
        self.message = f'A {self.enemy.name} attacks you!'

    def attack(self):
        if self._combat_over:
            return

        gs = self._gs

        # Player attacks
        play_sound('attack')
        self.enemy.health -= self.weapon_damage
        self.enemy_hp = max(0, self.enemy.health)
        self.message = f'You deal {self.weapon_damage} damage!'

        if self.enemy.health <= 0:
            self._combat_over = True
            self.message = f'You defeated the {self.enemy.name}!'
            del gs.active_enemies[self.enemy_pos]
            gs.killed_enemies.append(list(self.enemy_pos))
            gs.message = f'Defeated the {self.enemy.name}!'
            self.enemy_killed = True
            Clock.schedule_once(self._return_to_game, 1.0)
            return

        # Enemy attacks back
        actual = calc_damage(self.enemy.damage, self.defense)
        gs.health -= actual
        self.player_hp = max(0, gs.health)
        play_sound('hit')
        self.message += f'  {self.enemy.name} hits for {actual}!'

        if gs.health <= 0:
            self._combat_over = True
            gs.message = 'You died!'
            Clock.schedule_once(self._game_over, 1.0)

    def run_away(self):
        if self._combat_over:
            return

        gs = self._gs
        actual = calc_damage(self.enemy.damage, self.defense)
        gs.health -= actual
        self.player_hp = max(0, gs.health)
        play_sound('hit')
        gs.message = f'Fled from the {self.enemy.name}!'

        if gs.health <= 0:
            self._combat_over = True
            Clock.schedule_once(self._game_over, 0.5)
        else:
            self._return_to_game()

    def _return_to_game(self, *args):
        if self.enemy_killed:
            gs = self._gs
            gs.player_y, gs.player_x = self.enemy_pos
        self.manager.current = self._return_screen

    def _game_over(self, *args):
        play_sound('lose')
        end = self.manager.get_screen('end')
        end.result = 'GAME OVER: You were killed.'
        self.manager.current = 'end'
