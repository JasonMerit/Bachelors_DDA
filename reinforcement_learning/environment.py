import numpy as np
import gymnasium as gym
from gymnasium import spaces

from game.display import Display
from game.endless_runner import EndlessRunner

class EndlessRunnerEnv(gym.Env):
    """The purpose of the environment is to provide a standard interface for the 
    agent to interact with the game. Display enherits from EndlessRunner, so it
    can be used to run the game with rendering."""

    def __init__(self, render=False, truncated=True):
        self.game = Display() if render else EndlessRunner()
        self.game.set_difficulty(10)
        self.action_space = spaces.Discrete(4)
        # self.observation_space = spaces.Discrete(1)
        self.observation_space = spaces.Box(low=0, high=1000, shape=(3,), dtype=np.float16)
        # self.observation_space = spaces.Box(low=0, high=1000, shape=(5,), dtype=np.float16)
        self.step_count = 0
        self.max_steps = 1000

        self._truncate = lambda: self.step_count >= self.max_steps if truncated else False

    def step(self, action):
        """Actions:
        0: Do nothing
        1-3: Jump ranges from short to long
        """
        self.step_count += 1
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
        # reward = self.game.player.cleared_platforms - cleared_platforms
        # reward = 0 if terminated else 1
        reward = -100 if terminated else 1
        return self._state(), reward, terminated, self._truncate(), {}
    
    def reset(self, seed=None):
        super().reset(seed=seed)
        self.game.reset(seed)
        self.step_count = 0
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
        x1 = topright[0] - self.game.player.right
        dx = topleft[0] - topright[0]
        dy = topleft[1] - topright[1]
        return np.array([x1, dx, dy]).astype(np.float16)
        # return np.array([topright[0], topright[1], topleft[0], topleft[1]]).astype(np.float16)
        # return np.array([self.game.player.is_floor, topright[0], topright[1], topleft[0], topleft[1]]).astype(np.float16)

class DumbEnv(gym.Env):
    max_steps = 10

    def __init__(self, render=False):
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Discrete(2)
    
    def step(self, action):
        self.step_count += 1
        reward = int(action == self.last_observation)
        self.last_observation = self.observation_space.sample()
        truncated = self.step_count >= self.max_steps
        return np.array(self.last_observation).astype(np.float32), reward, False, truncated, {}
    
    def reset(self, seed=None):
        self.step_count = 0
        self.last_observation = self.observation_space.sample()
        return np.array(self.last_observation).astype(np.float32), {}
    
    def render(self, state=None):
        pass

    def close(self):
        pass


# from stable_baselines3.common.env_checker import check_env
# check_env(env, warn=True)
    # https://colab.research.google.com/github/araffin/rl-tutorial-jnrr19/blob/sb3/5_custom_gym_env.ipynb#scrollTo=1CcUVatq-P0l
# https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html