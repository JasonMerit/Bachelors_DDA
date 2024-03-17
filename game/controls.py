import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
from math import floor, log10

from game.config import Config
from game.actions import key_actions

class Controller:
    def __init__(self, actions={}):
        self.actions = actions
        self.clock = pg.time.Clock()
    
    def is_event_trigger(self, action, event, trigger_type, triggers):
        return action in self.actions and event.type == trigger_type and event.key in triggers

    def get_actions(self):
        for event in pg.event.get():
            for action, (trigger_type, triggers) in key_actions.items():
                if self.is_event_trigger(action, event, trigger_type, triggers):
                    yield self.actions[action]
    
    def handle_events(self):
        for action in self.get_actions():
            action()
        self.clock.tick(Config.FPS)

    @staticmethod
    def increase_speed():
        k = 10 ** int(floor(log10(abs(Config.FPS))))
        Config.FPS += k
        Config.FPS = min(10000, Config.FPS)
    
    @staticmethod
    def decrease_speed():
        k = 10 ** int(floor(log10(abs(Config.FPS - 1))))
        Config.FPS -= k
        Config.FPS = max(4, Config.FPS)
