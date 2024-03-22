
class CheaterAgent():
    from game.config import Config
    from game.entities import Player, Platform

    player_left = Player.init_pos[0] - Player.size
    speed = Platform.scroll_speed
    
    def __init__(self, verbose=False):
        self.verbose = verbose

    def predict(self, state):
        action = 0
        # is_floor, x1, y1, x2, y2 = state
        x1, y1, x2, y2 = state

        # cast to int
        # x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Stay if not on floor or not close to edge
        # print(x1)
        if self.player_left + self.speed < x1:  
        # if not is_floor or self.player_left + self.speed < x1:  
            return action
        
        # print(x1 - self.speed, self.player_left)
        # quit()
        dx, dy = x2 - x1, y2 - y1

        # Next platform is connected to the current platform
        if dx == dy == 0:  
            return action
        
        return 3
        if dy > 0:
            return 3

        # Action function
        f = dy + dx // 2

        if f > 140:
            action = 3
        elif f < 0:
            action = 1
        else:
            action = 2

        if self.verbose:
            print(f, action)
        return action
    