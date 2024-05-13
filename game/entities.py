from abc import ABC, abstractmethod

class Platform(ABC):
    """x and top define position, representing the top left corner of the platform.
    """
    scroll_speed = 5
    id = 0
    def __init__(self, topleft, width):
        self.x, self.top = topleft  # top left corner, so top is minimum y for clear collision
        self.width = width
        Platform.id += 1
        self.id = Platform.id
        self.obstacle = None
    
    @property 
    def topleft(self):
        return (self.x, self.top)    
    
    @property
    def topright(self):
        return (self.x + self.width, self.top)

    @property
    def right(self):
        return self.x + self.width

    @property
    def left(self):
        return self.x
    
    def move(self):
        self.x -= self.scroll_speed
    
    @abstractmethod
    def offset_player(self, player):
        pass
    
    def outline(self, invert=False):
        pass # for debugging

    def __repr__(self):
        return f"Platform: {self.id}, {self.topleft}, {self.width}"
    

class Flat(Platform):
    
    def offset_player(self, player):
        """Check if player is on the platform."""
        if player.is_floor:
            return
        
        if player.y < self.top:  
            player.y = self.top
            player.is_floor = True
            player.angle = 0

from math import cos, tan, radians
import random
class Slope(Platform):
    pass
    def __init__(self, topleft, width):
        super().__init__(topleft, width)
        self.angle = 25
        # self.angle = random.randint(15, 35)
        # self.angle *= random.choice([-1, 1])
        self.slope = tan(radians(self.angle))
        self.dy = self.slope * Platform.scroll_speed

        positive = int(self.angle > 0)

        # To handle both positive and negative slopes, define
        self._right_tip = topleft[1] + width * self.slope * positive
        self._left_tip = topleft[1] + width * self.slope * (1 - positive)

        # for negative slope, offset platform down
        
        # random angle in (15, 45)
        # self.radians = radians(self.angle)
        # self.slope = tan(self.radians)
        # self.width = width * cos(self.radians)
    
    @property
    def topright(self):
        return (self.x + self.width, self._right_tip)
    
    @property
    def topleft(self):
        return (self.x, self._left_tip)

    def offset_player(self, player):
        """Position player atop slope."""
        if player.is_floor:
            return

        top = self.top + int(self.slope * (player.x - self.left - 15))  # 15, because middle of player is offset?
        if player.y < top:
            player.y = top
            player.is_floor = True
            player.angle = -self.angle


class Obstacle():
    scroll_speed = 5
    width = 30
    height = 20
    
    def __init__(self, platform):
        self.x = platform.right - platform.width // 2 - self.width // 2
        self.bot = platform.top
        self.top = self.bot + self.height

    @property
    def left(self):
        return self.x
    
    @property
    def right(self):
        return self.x + self.width

    def move(self):
        self.x -= self.scroll_speed
