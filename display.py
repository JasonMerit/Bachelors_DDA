import pygame as pg
from pygame.color import Color
from pygame.surface import Surface
from pygame.sprite import Sprite, Group
import random, os, time

from endless_runner import EndlessRunner, Platform, Player
from config import *

from math import sqrt

FONT = "rockwell"
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".TTF"):
            FONT = os.path.join(root, file)[2:]
            break
        
def blit_rotate(surf, image, topleft, angle):
    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

def random_color():
    return (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150))    

def lerp_color(color1, color2, t):
    return [x + (y-x) * t for x, y in zip(Color(color1), Color(color2))]

class Display(EndlessRunner):
    pg.init()

    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Runner")

    clock = pg.time.Clock()
    # font_style = pg.font.SysFont(None, 30)
    # font_big = pg.font.SysFont("rockwell", 50)
    font_big = pg.font.Font(FONT, 50)
    # font_big = pg.font.Font("ROCK.TTF", 50)
    # font_style_small = pg.font.SysFont(None, 20)
 
    def __init__(self):
        self.sprites = Group()
        super().__init__()
    
    def reset(self):
        self.sprites.empty()
        self.sprites.add(self.player)
        super().reset()
    
    def close(self):
        pg.quit()
    
    def tick(self):
        # Process events, tick the game, and update sprites
        self.process_events()
        return super().tick()
        # self.render()
        
    def render(self):
        self.screen.fill(BLACK)
        self.sprites.update(self.screen)
        
        # Draw score
        self.score += 1
        msg = self.font_big.render(f'{self.score} m', True, GREY)
        self.screen.blit(msg, (WIDTH - msg.get_width() - 20, 20))

        # Draw death count
        msg = self.font_big.render(f'{self.deaths} deaths', True, GREY)
        self.screen.blit(msg, (20, 20))

        pg.display.flip()
        self.clock.tick(FPS)
    
    def construct_player(self, pos, size):
        player = super().construct_player(pos, size)
        player_sprite = PlayerSprite(player)
        return player_sprite
    
    def construct_platform(self, topleft, level=0):
        platform = super().construct_platform(topleft, level=level)
        color = GREEN if level else random_color()
        platform_sprite = PlatformSprite(platform, color)
        self.sprites.add(platform_sprite)
        return platform_sprite

    def remove_platform(self):
        platform = self.platforms.pop(0)
        self.sprites.remove(platform)

    def process_events(self):
        global FPS
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                if event.key == pg.K_r:
                    self.reset()
                elif event.key == pg.K_RETURN:
                    Platform.scroll_speed += 1

                elif event.key == pg.K_s and pg.key.get_mods() & pg.KMOD_CTRL:
                    path = "assets/screenshots"
                    pg.image.save(self.screen, f"{path}/{len(os.listdir(path))}.png")
                elif event.key == pg.K_DOWN:
                    
                    FPS -= 30
                    FPS = max(30, FPS)
                    # change screen caption
                    pg.display.set_caption(f"Canabalt - {FPS}")
                elif event.key == pg.K_UP:
                    
                    FPS += 30
                    FPS = min(30*100, FPS)
                    pg.display.set_caption(f"Canabalt - {FPS}")
                # elif event.key == pg.K_RETURN:
                #     print()
                #     for platform in self.platforms:
                #         print(platform)
                elif event.key == pg.K_p:
                    paused = True
                    while paused:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                pg.quit()
                                quit()
                            elif event.type == pg.KEYDOWN:
                                if event.key == pg.K_ESCAPE:
                                    pg.quit()
                                    quit()
                                if event.key == pg.K_p:
                                    paused = False
            
            self.player.process_event(event)
            # |-|--|--|-|- rhythm 

class PlatformSprite(Platform, Sprite):
    font = pg.font.Font(FONT, 50)

    def __init__(self, platform, color):
        super().__init__(platform.topleft, platform.width, level=platform.is_rest_area)
        Sprite.__init__(self)

        # self.surface = pg.Surface((platform.width, HEIGHT))
        # t0 = time.time()
        self.surface = pg.Surface((platform.width, HEIGHT))
        # self.surface = pg.Surface((platform.width, HEIGHT)).convert()
        # self.surface = pg.Surface((platform.width, HEIGHT)).convert_alpha()
        # print(f'Time: {time.time() - t0:.2f}')
        self.rect = self.surface.get_rect()
        self.surface.set_colorkey((0, 0, 0))
        pg.draw.rect(self.surface, WHITE, self.rect, 0, 10)
        shade_color = lerp_color(color, WHITE, 0.4)
        pg.draw.rect(self.surface, shade_color, self.rect, 15, 10)
        # pg.draw.rect(self.surface, SHADE, self.rect, 15, 10)

        self.surface.fill(color, special_flags=3)  # 0.63

        if self.is_rest_area:
            # font = pg.font.Font("ROCK.TTF", 50)
            # font = pg.font.SysFont("rockwell", 50)
            msg = self.font.render(f"LEVEL {self.is_rest_area}", True, GREY)
            x = (msg.get_width() - self.width // 4) / 2  
            y = (self.top - msg.get_height()) / 2
            self.surface.blit(msg, (x, y))
            

    def update(self, screen : Surface):
        screen.blit(self.surface, (self.x, HEIGHT - self.top))

class PlayerSprite(Player, Sprite):
    
    def __init__(self, player):
        Sprite .__init__(self)
        super().__init__(player.pos, player.size)
        self.surface = Surface((self.size, self.size)).convert_alpha()
        self.surface.fill(WHITE)        
        # add shade to image

        shade = (0, 0, 0, 100)
        line_width = self.size // 8
        
        # horinzontal
        shadow = Surface((self.size, line_width)).convert_alpha()
        shadow.fill(shade)
        self.surface.blit(shadow, (0, 0))
        self.surface.blit(shadow, (0, self.size - line_width))

        # Vertical
        shadow = Surface((line_width, self.size - 2 * line_width)).convert_alpha()
        shadow.fill(shade)
        self.surface.blit(shadow, (0, line_width))
        self.surface.blit(shadow, (self.size - line_width, line_width))

        # self.rect.bottomleft = self.pos[0], HEIGHT - self.pos[1] - self.size
    
    @property
    def topleft(self):
        return (self.x, HEIGHT - self.y - self.size)

    def update(self, screen : Surface):
        if self.angle_speed == 0:
            screen.blit(self.surface, self.topleft)
        else:
            self.angle += self.angle_speed
            blit_rotate(screen, self.surface, self.topleft, -self.angle)
    
    def fall(self):
        super().fall()
        
        # First phase constant speed
        # h = v_0t_1 
        v, t1 = self.jump_speed, self.max_hold_frames
        h = v*t1
        
        # Second phase constant acceleration
        # y = h + v_1t_2 - 1/2gt_2^2 = 0
        g = self.gravity
        t2 = (v + sqrt(v**2 + 2 * g * h)) / g  # positive root

        t = t1 + t2
        omega = 90 / t
        self.angle_speed = omega

        # d = self.jump_speed ** 2 + 2 * self.gravity * self.jump_speed * self.max_hold_frames
        # tom = (self.jump_speed + sqrt(d)) / self.gravity + self.max_hold_frames  # time of flight
        # omega = self.rotations * 90 / tom
        # self.angle_speed = omega

    def process_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and self.is_floor:
                self.jump()
                
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                self.is_holding = False  # Release jump from keyup


def main():
    display = Display()
    display.reset()

    while True:
        done = display.tick()
        if done:
            display.reset()
        display.render()
        
if __name__ == "__main__":
    main()