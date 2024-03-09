import pygame as pg
import numpy as np
import random

from config import *
from rhythm_generator import LevelGenerator

random.seed(SEED)
np.random.seed(SEED)

class Display():
    pg.init()
    BLACK, WHITE = (24, 24, 24), (202, 202, 202)
    width, height = 800, 600
    ratio = width / 30

    display = pg.display.set_mode((width, height))
    display.fill(BLACK)
    pg.display.set_caption("Runner")
    clock = pg.time.Clock()
    font_style = pg.font.SysFont(None, 30)
    font_style_small = pg.font.SysFont(None, 20)
    
    def update(self, rhythm, geometry):
        self.display.fill(self.BLACK)
        self.draw_rhythm(rhythm)
        self.draw_geometry(geometry, rhythm[0])
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
        duration, jumps = rhythm
        self.message(f"Rhythm  ", (x, y), self.WHITE, "right")
        pg.draw.line(self.display, self.WHITE, (x, y), (x + duration * self.ratio, y), 4)

        # Draw vertical hatches at each jump
        ratio = self.ratio
        for i in range(len(jumps)):
            dx = x + jumps[i][0] * ratio
            self.message(f"{jumps[i][0]} ", (dx, y-20), self.WHITE, small = True)
            pg.draw.line(self.display, self.WHITE, (dx, y - 10), (dx, y + 10), 3)

        # Draw a unit length line
        y -= 40
        self.message(f"Unit ", (x, y), self.WHITE, "right")
        pg.draw.line(self.display, self.WHITE, (x, y), (x + UNIT * ratio, y), 4)
    
    def draw_geometry(self, geometry, duration):
        x0, y = self.width / 5, self.height * 1.4 / 5
        start = x0

        # start and stop of each platform deifnd by jump and hold_down time
        for x, t in geometry:  
            stop = x0 + x * self.ratio
            pg.draw.line(self.display, self.WHITE, (start, y), (stop, y), 10)
            start = stop + t * self.ratio

        if start < x0 + duration * self.ratio - 1:
            pg.draw.line(self.display, self.WHITE, (start, y), (x0 + duration * self.ratio, y), 10)

        # Write 'Rhythm' to the left of the line    
        self.message(f"Geometry #{len(geometry)}  ", (x0, y), self.WHITE, "right")



def process_events():
    for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                elif event.key == pg.K_RETURN:
                    return action()
                    

action_count = 1
def action(level_generator: LevelGenerator):
    global action_count
    print(f"\nAction {action_count}")
    res1 = level_generator.get_rhythm(pattern="random")
    print(f'Rhythm {res1}')

    res2 = level_generator.get_geometry(res1)
    print(f'Geometry    {res2}')

    
    action_count += 1
    return res1, res2

def test():
    # Determine seed
    global SEED
    for _ in range(PRE_ACTIONS):
        print(f"\nSEED {SEED}")
        random.seed(SEED)
        np.random.seed(SEED)
        action()
        SEED += 1


def main():
    display = Display() if not DEBUG else None
    level_generator = LevelGenerator()

    print(f"{SEED=}")
    for _ in range(PRE_ACTIONS):
        rhythm, geometry = action(level_generator)
        process_events() 

    if display:
        while True:
            if res := process_events():
                display.update(*res)

if __name__ == "__main__":
    main()

