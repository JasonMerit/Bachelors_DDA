from util import *
from config import *
from math import sqrt

class Platform():
    """x and top define position, representing the top left corner of the platform.
    """
    scroll_speed = 5
    rest_area_width = 300
    id = 0
    def __init__(self, topleft, width, level = 0):
        self.x, self.top = topleft
        self.width = width
        self.is_rest_area = level
        Platform.id += 1
        self.id = Platform.id
    
    @classmethod
    def rest_area(cls, topleft, level):
        return cls(topleft, cls.rest_area_width, level)
    
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
    
    def __repr__(self):
        return f"Platform: {self.id}, {self.topleft}, {self.width}"

class Player():
    """x and y define position, representing the BOTTOM left corner of the player.
    Since platform uses TOP left corner, this allows for easy collision detection.
    TODO: replace with vector when dashing"""
    
    init_pos = WIDTH // 8, 100
    gravity = 2
    speed = 0
    _is_floor = True
    size = 30
    
    # jumping
    jump_speed = 15
    is_holding = False
    max_hold_frames = 10
    jump_times = [42, max_hold_frames, max_hold_frames // 2, 0]  # 42 is for no jump, but index is never 0
    hold_frames = 0
    jump_threshold = 10

    # Rotation (visual)
    angle = 0
    angle_speed = 0
    rotations = 2

    # pre computations for physics constraints
    max_jump_height = jump_speed * max_hold_frames + 0.5 * jump_speed ** 2 / gravity
    up_time = jump_speed / gravity + max_hold_frames  # Increasing position time
    fly_time = lambda self, delta_y: self.up_time + sqrt(2 * delta_y / self.gravity)

    def __init__(self):
        self.x, self.y = self.init_pos
    
    def reset(self):
        self.x, self.y = self.init_pos
        self.speed = 0
        self._is_floor = True
        self.is_holding = False
        self.angle = 0
        self.angle_speed = 0
    
    @property
    def pos(self):
        return self.x, self.y

    @property
    def right(self):
        return self.x
    
    @property
    def left(self):
        return self.x - self.size
    
    @property
    def is_floor(self):
        return self._is_floor
    
    @is_floor.setter
    def is_floor(self, value):
        self._is_floor = value
        if value is True:
            self.speed = 0
            self.angle = 0
            self.angle_speed = 0
    
    @is_floor.getter
    def is_floor(self):
        return self._is_floor
    
    def move(self):
        # # Apply gravity if not on floor
        if not self.is_floor:  
            # Holding jump
            if self.is_holding:
                self.hold_frames += 1
                if self.hold_frames >= self.max_hold_frames:
                    self.is_holding = False  # Release jump from expired hold
                    self.fall()
            else:
                self.speed -= self.gravity
                # self.angle_speed = 100  # Rotate to simulate falling

            self.y += self.speed
        # print(f'y: {self.y}')
    
    def jump(self, hold_frames=None):
        """Jump and hold jump if long is True. 
        Written this way to account for agent's jump.
        
        :param hold_frames: Number of frames to hold jump
        """
        self.is_holding = True
        if hold_frames is None:  # Human player
            self.hold_frames = 0
        else:
            self.hold_frames = self.jump_times[hold_frames]  # -1 is for no jump, but action is never 0
        self.speed = self.jump_speed
        self.leave_floor()
        # end()
    
    def leave_floor(self):
        """Leave the floor (and start rotating).
        Called when jump is pressed or when falling off a platform.
        """
        self.is_floor = False
    
    def fall(self):
        """Called when jump is released and gravity takes over."""
        pass  # Implemented in subclass

    def floor_collision(self, height):
        if self.y < height:  
            self.y = height
            self.is_floor = True