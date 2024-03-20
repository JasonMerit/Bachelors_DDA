import numpy as np
import gymnasium as gym
from gymnasium import spaces

from game.display import Display
from game.endless_runner import EndlessRunner

class EndlessRunnerEnv(gym.Env):
    """The purpose of the environment is to provide a standard interface for the 
    agent to interact with the game. Display enherits from EndlessRunner, so it
    can be used to run the game with rendering."""

    def __init__(self, render=False):
        self.game = Display() if render else EndlessRunner()
        self.action_space = spaces.Discrete(4)
        # self.observation_space = spaces.Discrete(1)
        self.observation_space = spaces.Box(low=0, high=1000, shape=(4,), dtype=np.float16)
        # self.observation_space = spaces.Box(low=0, high=1000, shape=(5,), dtype=np.float16)

    def step(self, action):
        """Actions:
        0: Do nothing
        1-3: Jump ranges from short to long
        """
        cleared_platforms = self.game.player.cleared_platforms
        if action > 0:
            self.game.take_action(action - 1)
        
        # From jumping or falling off ledge after waiting
        # keep ticking until player is on floor or game is over
        terminated = self.game.tick()
        while not self.game.player.is_floor and not terminated:
            terminated = self.game.tick()
            self.render()

        # terminated = self.game.tick()  # Remember truncation
        truncated = False 
        reward = self.game.player.cleared_platforms - cleared_platforms
        # reward = 1 if not terminated else -1
        assert self.game.player.is_floor or terminated, f"Player is not on floor!"
        return self._state(), reward, terminated, truncated, {}
    
    def reset(self, seed=None):
        super().reset(seed=seed)
        self.game.reset(seed)
        return self._state(), {}
    
    def render(self, state=None):
        self.game.render(state)
    
    def close(self):
        self.game.close()
    
    def set_render(self, render):
        self.game = Display() if render else EndlessRunner()

    def _state(self):
        """Return the state consisting of the tuple
        - player on floor (0, 1)
        - topright of the first platform
        - topleft of the second platform
        """
        # First platform with platform_left > player_right
        index = 0
        plat1 = self.game.platforms[index]
        while plat1.right < self.game.player.left:
            index += 1
            plat1 = self.game.platforms[index]
        plat2 = self.game.platforms[index + 1]

        topright = plat1.topright
        topleft = plat2.topleft
        return np.array([topright[0], topright[1], topleft[0], topleft[1]]).astype(np.float16)
        # return np.array([self.game.player.is_floor, topright[0], topright[1], topleft[0], topleft[1]]).astype(np.float16)


# from stable_baselines3.common.env_checker import check_env
# check_env(env, warn=True)
    # https://colab.research.google.com/github/araffin/rl-tutorial-jnrr19/blob/sb3/5_custom_gym_env.ipynb#scrollTo=1CcUVatq-P0l
# https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html