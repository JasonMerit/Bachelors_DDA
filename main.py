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
        if plat2.is_rest_area or self.player.y == plat2.top:
            return
        if self.player.right > plat1.right:
            # Determine jump type
            if plat1.top < plat2.top - 100:
                self.jump(0)
            elif plat1.top < plat2.top - 200:
                self.jump(1)
            else:
                self.jump(2)
        
    def jump(self, jump_type):
        if not self.player.is_floor:  # No jumping while in the air
            return
        self.player.is_holding = True
        self.player.hold_frames = [10, 7, 4][jump_type]
        self.player.speed = self.player.jump_speed
        self.player.fall()




if __name__ == '__main__':
    game = display.Display()
    agent = Agent(game)

    while True:
        agent.step()
        game.tick()
        