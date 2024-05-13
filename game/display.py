from random import randint
import pygame as pg
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from pygame.sprite import Group
from collections import deque

from game.endless_runner import EndlessRunner
from game.config import Config
from game.sprites import FlatSprite, SlopeSprite, PlayerSprite, _SlopeSprite, ObstacleSprite

FONT = "game/ROCK.TTF"
        
# def blit_rotate(surf, image, topleft, angle):
#     rotated_image = pg.transform.rotate(image, angle)
#     new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
#     surf.blit(rotated_image, new_rect.topleft)

def random_color():
    return (randint(100, 150), randint(100, 150), randint(100, 150))    

# def lerp_color(color1, color2, t):
#     return Color([x + (y-x) * t for x, y in zip(Color(color1), Color(color2))])

class Display(EndlessRunner):
    # Attributes overwritten
    player : PlayerSprite
    
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((Config.width, Config.height))
        pg.display.set_caption(Config.caption)

        self.clock = pg.time.Clock()
        # font_style = pg.font.SysFont(None, 30)
        # font_big = pg.font.SysFont("rockwell", 50)
        self.font_big = pg.font.Font(FONT, 50)
        # font_big = pg.font.Font("ROCK.TTF", 50)
        # font_style_small = pg.font.SysFont(None, 20)
        self.sprites = Group()
        super().__init__()

        self.highscore = 0
        self.history = deque(maxlen=100)
    
    @staticmethod
    def play_recordings(histories, fps=60):
        pg.init()
        screen = pg.display.set_mode((Config.width, Config.height))
        clock = pg.time.Clock()
        for history in histories:
            for h in history:
                pg.surfarray.blit_array(screen, h)
                pg.display.flip()
                clock.tick(fps)
        
        pg.quit()
    
    @staticmethod
    def play_random_states(random_states, fps=60):
        pg.init()
        game = Display()
        clock = pg.time.Clock()
        for state in random_states:
            game.game_master.set_state(state)
            clock.tick(fps)
        
        pg.quit()
    
    def reset(self):
        self.sprites.empty()
        # self.sprites.add(self.player)
        if self.player.cleared_platforms > self.highscore:
            self.highscore = self.player.cleared_platforms
        super().reset()
    
    def close(self):
        pg.quit()
    
    def render(self, state=None, step_count=0, debug=True):
        self.screen.fill(Config.BLACK)
        self.sprites.update(self.screen, debug)
        self.player.update(self.screen, debug)  # Player infront of platforms
        
        # Draw difficulty under FPS
        msg = self.font_big.render(f'{self.difficulty}', True, Config.GREY)
        self.screen.blit(msg, (20, 20))
        
        # Draw death count
        msg = self.font_big.render(f'{self.deaths} deaths', True, Config.GREY)
        self.screen.blit(msg, (20, 70))

        # Draw player.cleared_platforms
        msg = self.font_big.render(f'{self.player.cleared_platforms} / {self.highscore}', True, Config.GREY)
        self.screen.blit(msg, (Config.width - msg.get_width() - 20, 20))

        # Draw FPS
        msg = self.font_big.render(f'{Config.FPS}', True, Config.GREY)
        self.screen.blit(msg, (Config.width // 2, 20))

        
        # Draw player trajectory
        # self.player.draw_curve(self.screen, self.platforms[:2])
        if debug is True:

            # Draw state
            # if state is not None:
            #     x1, dx, dy = state.astype(int)
            #     x1 += self.player.left
            #     pg.draw.circle(self.screen, Config.WHITE, (x1, Config.height - self.player.y), 5)
            #     pg.draw.circle(self.screen, Config.WHITE, (x1 + dx, Config.height - self.player.y - dy), 5)
            
            # Draw stepcount
            msg = self.font_big.render(f'{step_count}', True, Config.GREY)
            self.screen.blit(msg, (Config.width - msg.get_width() - 20, 70))

        pg.display.flip()
        self.history.append(pg.surfarray.array3d(self.screen))
        self.clock.tick(Config.FPS)
    
    def construct_player(self):
        return PlayerSprite()
    
    def construct_platform(self, topleft, width=300, flat=False):
        platform_sprite = FlatSprite(topleft, width, random_color())
        # if flat:
        #     platform_sprite = FlatSprite(topleft, width, random_color())
        # else:
        #     r = randint(0, 3) if not Config.FLAT else 1
        #     if r:
        #         platform_sprite = FlatSprite(topleft, width, random_color())
        #     else:
        #         platform_sprite = _SlopeSprite(topleft, width, random_color())        
        self.sprites.add(platform_sprite)
        return platform_sprite

    def remove_platform(self):
        platform = self.platforms.pop(0)
        self.sprites.remove(platform)
        if platform.obstacle:
            self.sprites.remove(platform.obstacle)
            self.obstacles.pop(0)

    def construct_obstacle(self, platform) -> ObstacleSprite:
        obstacle_sprite = ObstacleSprite(platform)
        self.sprites.add(obstacle_sprite)
        return obstacle_sprite


