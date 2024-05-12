from typing import Tuple

from game.game_master import GameMaster
from game.config import Config
from game.util import *
from game.player import Player
from game.entities import Platform, Flat, Slope


class EndlessRunner():
    margin = 200  # Offset from right screen for smooth scrolling

    def __init__(self):
        self.game_master = GameMaster()
        self.max_height, self.min_height = Config.height - 100, 100
        self.min_gap = 45

        # Player
        self.player : Player = self.construct_player()
        self.deaths = -1

        self.history = []  # Display
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.game_master.set_difficulty(difficulty)
    
    def reset(self, seed=None):
        # if seed is not None:
        #     self.game_master.seed(seed)
        self.deaths += 1
        self.score = 0
        self.level = 1

        # List of platforms that are moved every tick
        self.platforms = [self.construct_platform(Player.init_pos, flat=True)]
        self.platforms[0].outline() # debug
        self._fill_platforms()

        # Player
        self.player.reset(self.platforms)
    
    # def get_random_state(self):
    #     return self.game_master.get_state()

    def tick(self):
        self._update_positions()

        if self.player.tick() is True:
            if Config.GOD:
                self.deaths += 1
                return False
            return True  # Terminated
        
        self.score += 1  # Increase score every tick
        return False  # Terminated (replace all self.restart() with return True)


    def _update_positions(self):
        """Update player and platforms positions. Also remove off screen platform."""

        for platform in self.platforms:
            platform.move()
        
        if self.platforms[0].right < 0:
            if Config.VERBOSE:
                print("Removing", self.platforms[0])
            
            self.remove_platform()
            self._add_platform()
    
    def _fill_platforms(self):
        """Fill the screen with platforms."""
        while self.platforms[-1].right < Config.width + self.margin:
            self._add_platform()
        self._add_platform()

    def _add_platform(self):
        """Add a new platform to the end of the list."""
        start = self.platforms[-1].topright
        platform = self.game_master.next_platform(*start)
        self.platforms.append(self.construct_platform(*platform))

    # def _create_level(self, count=3):
    #     """Create a new level of platforms and rest area.
    #     :param count: number of platforms in the level
    #     :return: list of platforms
    #     """
    #     self.level += 1
    #     start = self.platforms[-1].topright
    #     platforms = self.game_master.get_level(start, count)
    #     res = []
    #     for plat in platforms[:-1]:
    #         topleft, width = plat
    #         res.append(self.construct_platform(topleft, width))
    #     platforms[-1] = platforms[-1][0], self.rest_width
    #     res.append(self.construct_platform(*platforms[-1]))
    #     return res
        
    ### ===== Player methods ===== ###
    def jump(self):
        if self.player.is_floor:
            self.player.jump()
    
    def jump_release(self):
        if not self.player.is_floor:
            self.player.jump_release()

    ### ===== Agent methods ===== ###
    def take_action(self, action):
        """Actions: 0-2: Jump ranges from short to long"""
        if self.player.is_floor:
            self.player.jump(action)

    ### ===== Inherited by Display ===== ###
    def render(self, state=None, step_count=0, debug=False):
        pass  # Implemented in Display

    def close(self):
        pass  # Implemented in Display

    def construct_player(self):
        return Player()
    
    def construct_platform(self, topleft, width=300, flat=True) -> Platform:
        return Flat(topleft, width)

    def remove_platform(self):
        self.platforms.pop(0)

