import gym
from gym import spaces

from ai.agent import Agent

class EndlessRunnerEnv(gym.Env):
    """The purpose of the environment is to provide a standard interface for the 
    agent to interact with the game. Display enherits from EndlessRunner, so it
    can be used to run the game with rendering."""

    def __init__(self, game):
        self.game = game
        
        self.action_space = spaces.Discrete(4)
        # self.observation_space = spaces.Discrete(1)
        # self.observation_space = spaces.Box(low=0, high=1000, shape=(5, 1), dtype=np.uint8)

    def step(self, action):
        """Actions:
        0: Do nothing
        1-3: Jump ranges from short to long
        """
        if action:
            self.game.take_action(action)

        terminated = self.game.tick()  # Remember truncation
        reward = 1 if not terminated else -1
        return self._state(), reward, terminated, {}
    
    def reset(self):
        self.game.reset()
        return self._state()
        # return self.get_state()
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
        return self.game.player.is_floor, topright[0], topright[1], topleft[0], topleft[1]

def main():
    env = EndlessRunnerEnv()
    agent = Agent()
    state = env.reset()
    while True:
        action = agent.get_action(state)
        # action = env.action_space.sample()
        state, reward, done, _ = env.step(action)
        if done:
            state = env.reset()
        env.render()

if __name__ == '__main__':
    main()
        