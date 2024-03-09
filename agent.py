
class Agent():
    def __init__(self, verbose=False):
        self.verbose = verbose

    def get_action(self, state):
        action = 0
        is_floor, x1, y1, x2, y2 = state
        
        if not is_floor or x1 >= 130:  # Jump if not on floor or close to the edge
            return action
        
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:  # Next platform is connected
            return action
        
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
    