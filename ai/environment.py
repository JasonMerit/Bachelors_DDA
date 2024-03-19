import numpy as np
import gymnasium as gym
from gymnasium import spaces

from game.endless_runner import EndlessRunner
from game.display import Display

class EndlessRunnerEnv(gym.Env):
    """The purpose of the environment is to provide a standard interface for the 
    agent to interact with the game. Display enherits from EndlessRunner, so it
    can be used to run the game with rendering."""

    def __init__(self, render=False):
        # super(EndlessRunnerEnv, self).__init__()
        self.game = Display() if render else EndlessRunner()
        
        self.action_space = spaces.Discrete(4)
        # self.observation_space = spaces.Discrete(1)
        self.observation_space = spaces.Box(low=0, high=1000, shape=(5,), dtype=np.uint16)

    def step(self, action):
        """Actions:
        0: Do nothing
        1-3: Jump ranges from short to long
        """
        if action:
            self.game.take_action(action)

        terminated = self.game.tick()  # Remember truncation
        truncated = False
        reward = 1 if not terminated else -1
        return self._state(), reward, terminated, truncated, {}
    
    def reset(self, seed=None):
        super().reset()
        self.game.reset()
        return self._state(), {}
    
    def render(self):
        self.game.render()
    
    def close(self):
        self.game.close()

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
        return np.array([self.game.player.is_floor, topright[0], topright[1], topleft[0], topleft[1]]).astype(np.uint16)
        return self.game.player.is_floor, topright[0], topright[1], topleft[0], topleft[1]


# from stable_baselines3.common.env_checker import check_env
# check_env(env, warn=True)
    # https://colab.research.google.com/github/araffin/rl-tutorial-jnrr19/blob/sb3/5_custom_gym_env.ipynb#scrollTo=1CcUVatq-P0l
# https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html