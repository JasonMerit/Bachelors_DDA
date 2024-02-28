import display
from gym import spaces

class Agent():
    
    def __init__(self, game):
        self.game = game
        self.player = self.game.player
        # self.game = er.Game()
        # self.game.restart()
    
    def step(self):
        plat1, plat2 = self.game.platforms[0], self.game.platforms[1]
        if self.player.right <= plat1.right or plat2.is_rest_area or self.player.y == plat2.top:
            return
        # dx, dy = plat2.topleft[0] - plat1.topright[0], plat2.topleft[1] - plat1.topright[1]
        # Determine jump type
        if plat1.top > plat2.top:
            self.jump(0)
        elif plat1.top < plat2.top:
            self.jump(2)
        else:
            self.jump(1)
        
    def jump(self, jump_type):
        if not self.player.is_floor:  # No jumping while in the air
            return
        self.player.is_holding = True
        self.player.hold_frames = [10, 7, 4][jump_type]
        self.player.speed = self.player.jump_speed
        self.player.fall()

class Environemt():
    
    def __init__(self):
        self.game = display.Display()
        self.agent = Agent(self.game)
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=255, shape=(self.game.height, self.game.width, 3), dtype=np.uint8)
    
    def step(self, action):
        self.agent.step()
        self.game.tick()
        return self.game.get_screen(), 0, False, {}
    
    def reset(self):
        self.game.restart()
        return self.game.get_screen()

if __name__ == '__main__':
    game = display.Display()
    game.restart()
    agent = Agent(game)

    while True:
        agent.step()
        game.tick()
        