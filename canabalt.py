import pygame as pg
from pygame.math import Vector2
import numpy as np
import random

from config import *

random.seed(SEED)
np.random.seed(SEED)

class Player(pg.sprite.Sprite):

    gravity = 1.0
    speed = 0.0
    ground_height = 500
    is_floor = False
    
    # jumping
    jump_speed = 15.0
    is_holding = False
    max_hold_time = 0.2
    hold_timer = 0.0
    jump_threshold = 10.0
    
    def __init__(self, size, color):
        pg.sprite.Sprite.__init__(self)
        self.image : pg.Surface = pg.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (100, self.ground_height - size / 2)
    
    @property
    def y(self):
        return self.rect.bottom
    
    def process_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                distance = self.ground_height - self.y
                # print(f'{distance = }, {self.speed = }')
                if self.is_floor or distance - 1.5*self.speed <= self.jump_threshold: 
                    self.is_holding = True
                    self.hold_timer = 0.0
                    self.jump()
                
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                self.is_holding = False
    
    def update(self, screen):
        # Apply gravity if not on floor
        if not self.is_floor:  
            
            # Holding jump
            if self.is_holding:
                self.hold_timer += DT
                if self.hold_timer >= self.max_hold_time:
                    self.is_holding = False
            else:
                self.speed += self.gravity

            # Move player
            self.rect.move_ip((0, self.speed))  
            
            # Floor check
            if self.rect.bottom > self.ground_height:  
                self.rect.bottom = self.ground_height
                self.is_floor = True
                # self.hold_timer = 0.0
            
        screen.blit(self.image, self.rect)
    
    def jump(self):
        self.speed = -self.jump_speed
        self.is_floor = False

class Game():
    pg.init()

    BLACK, WHITE = (24, 24, 24), (202, 202, 202)
    BLUE, GREY = (90, 95, 116), (179, 178, 194) 
    width, height = 800, 600
    screen = pg.display.set_mode((width, height))
    screen.fill(BLUE)
    pg.display.set_caption("Canabalt")

    clock = pg.time.Clock()
    font_style = pg.font.SysFont(None, 30)
    font_style_small = pg.font.SysFont(None, 20)

    player = Player(20, BLACK)

    def tick(self):
        self.process_events()
        

        self.screen.fill(self.BLUE)
        self.player.update(self.screen)
        pg.draw.rect(self.screen, self.GREY, (0, self.player.ground_height, self.width, self.height - self.player.ground_height))
        pg.display.update()
        
        self.clock.tick(FPS)

    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
            
            self.player.process_event(event)
                    
                
                
                
if __name__ == "__main__":
    game = Game()
    
    while True:
        
        game.tick()