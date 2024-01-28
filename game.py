import pygame as pg
import numpy as np
import random
from config import *

random.seed(SEED)
np.random.seed(SEED)

class Display():
    BLACK, WHITE = (24, 24, 24), (202, 202, 202)

    def __init__(self):
        pg.init()
        self.width = 800
        self.height = 600
        self.display = pg.display.set_mode((self.width, self.height))
        self.display.fill(self.BLACK)
        self.caption = pg.display.set_caption("Runner")
        self.clock = pg.time.Clock()
        self.font_style = pg.font.SysFont(None, 30)
        self.font_style_small = pg.font.SysFont(None, 20)

        self.rhythm_length = self.width * 3 / 5
    
    def update(self, rhythm, geometry):
        self.display.fill(self.BLACK)
        self.draw_rhythm(rhythm)
        self.draw_geometry(geometry)
        pg.display.update()
        # self.clock.tick(60)

    def message(self, msg : str, pos : tuple, color : tuple, align = "center", small = False):
        font = self.font_style_small if small else self.font_style
        self.msg = font.render(msg, True, color)
        x, y = pos[0], pos[1] - self.msg.get_height() / 2

        if align == "center":
            x -= self.msg.get_width() / 2
        elif align == "right":
            x -= self.msg.get_width()
        self.display.blit(self.msg, (x, y))
    
    def draw_rhythm(self, rhythm):
        x, y = self.width / 5, self.height / 5
        self.message(f"Rhythm  ", (x, y), self.WHITE, "right")
        pg.draw.line(self.display, self.WHITE, (x, y), (x + self.rhythm_length, y), 4)

        # Draw vertical hatches at each jump
        duration, jumps = rhythm
        ratio = self.rhythm_length / duration
        for i in range(len(jumps)):
            dx = x + jumps[i][0] * ratio
            self.message(f"{jumps[i][0]} ", (dx, y-20), self.WHITE, small = True)
            pg.draw.line(self.display, self.WHITE, (dx, y - 10), (dx, y + 10), 3)

        # Draw a unit length line
        y -= 40
        self.message(f"Unit ", (x, y), self.WHITE, "right")
        pg.draw.line(self.display, self.WHITE, (x, y), (x + UNIT * ratio, y), 4)
    
    def draw_geometry(self, geometry):
        x0, y = self.width / 5, self.height * 1.4 / 5
        start = x0
        ratio = self.rhythm_length / 10

        for x, t in geometry:
            stop = x0 + x * ratio
            pg.draw.line(self.display, self.WHITE, (start, y), (stop, y), 10)
            start = stop + t * ratio
        # pg.draw.line(self.display, self.WHITE, (start, y), (self.width, y), 10)
        pg.draw.line(self.display, self.WHITE, (start, y), (x0 + self.rhythm_length, y), 10)
        # print(f'{start = }, {x0 + self.rhythm_length}')
        # Write 'Rhythm' to the left of the line    
        self.message(f"Geometry #{len(geometry)}  ", (x0, y), self.WHITE, "right")

def get_rhythm(density = 4, duration = DURATION, pattern = "regular"):
    """Returns a rhythm of hatches. Rhythms are not constrained in any way.
    :param density: Number of hatches
    :param duration: Duration of the rhythm
    :param pattern: Pattern of hatches, either "regular" or "random"
    :return: A tuple of duration, [hatches, and type (hold_down times)]
    """
    if pattern == "regular":
        x = duration / (density + 1)
        hatches = [i * x for i in range(1, density + 1)]

    elif pattern == "random":    
        # sample unqiue random numbers from 0 to duration
        hatches = random.sample(np.arange(0, 10, 0.25).tolist(), 4)
        # hatches = [random.randint(0, duration / UNIT ) * UNIT for _ in range(density)]
        print(f'{hatches = }')


    # hold_down time UNIT / 0.5 / 0.75
    type = (np.random.randint(1, 4, density) * UNIT).tolist() 
    jumps = list(zip(hatches, type))
    jumps.sort()  # Sort by hatch and then type

    return duration, jumps
    # return duration, [hatches, type]

def get_geometry(rhythm : tuple):
    """Convert a rhythm into a geometry of jumps constrained by physics"""
    duration, jumps = rhythm
    jumps = jumps.copy()

    # If first too quick, remove it
    while jumps[0][0] <= UNIT:  
        jumps.pop(0)
    
    # If jump extends to next group, skip it
    while jumps[-1][0] + jumps[-1][1] >= DURATION - UNIT:  
        jumps.pop()

    # jump0 = jumps[0]
    geometry = [jumps[0]]
    for jump in jumps[1:]: # If jump to quick after prior, skip it
        if jump[0] - geometry[-1][0] > UNIT + geometry[-1][1]:
        # if jump[0] - jump0[0] > UNIT + UNIT * jump0[1]:  
            geometry.append((jump))
        # jump0 = jump
    
    return geometry

def process_events():
    if display is None:
        return
    
    for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                elif event.key == pg.K_RETURN:
                    action()

def action():
    res1 = get_rhythm(pattern="random")
    print(f'Rhythm {res1}')

    res2 = get_geometry(res1)
    print(f'Geometry    {res2}')

    if display:
        display.update(res1, res2)

def test():
    global SEED
    for _ in range(PRE_ACTIONS):
        print(f"\nSEED {SEED}")
        random.seed(SEED)
        np.random.seed(SEED)
        action()
        SEED += 1

display = Display() if DEBUG else None
action_count = 1
def main():
    global action_count
    print(f"{SEED=}")
    for _ in range(PRE_ACTIONS):
        print(f"\nAction {action_count}")
        action()
        action_count += 1

        process_events() 

    if display:
        while True:
            process_events()
        
if __name__ == "__main__":
    if DEBUG:
        test()
    else:
        main()
