import gym
from gym import spaces
from endless_runner import Game, Platform, Player

class GameEnv(gym.Env):
    
    action_space = spaces.Discrete(4)  # 3 jumps and 1 run
    observation_space = spaces.Discrete(4) # TODO

    game = Game()

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self):
        pass

    def close(self):
        pass
    