import pygame as pg

class Platform():
    x = 0
    def __init__(self, x):
        self.x = x
    
    def __str__(self) -> str:
        return f"Platform[x = {self.x}]"
    
    def move(self, x):
        self.x += 1

class Game():
    platforms = []
    def __init__(self):
        self.platforms.append(self.construct_platform())

    def tick(self):
        for platform in self.platforms:
            platform.move(1)

        self.platforms.append(self.construct_platform())  # Test adding platforms still draws them

    def construct_platform(self):
        return Platform(9)  # Non-zero x

    def remove_platform(self, platform):
        self.platforms.remove(platform)


class PlatformSprite(Platform):

    def __init__(self, platform):
        super().__init__(platform.x)
        pass

    def __str__(self) -> str:
        return "(Sprite)" + super().__str__()

    def add_internal(self, _):
        print("Added", self)
    
    def remove_internal(self, _):
        print("Removed", self)
    
    def update(self):
        print(self)

class Display(Game):
    pg.init()
    def __init__(self):
        self.sprites = pg.sprite.Group()
        super().__init__()
    
    def tick(self):
        super().tick()
        self.sprites.update()
        print("--------------------")
    
    def construct_platform(self):
        platform = super().construct_platform()
        platform_sprite = PlatformSprite(platform)
        self.sprites.add(platform_sprite)
        return platform_sprite

    def remove_platform(self, platform):
        super().remove_platform(platform)
        self.sprites.remove(platform)

display = Display()

# Check if the display is working
for _ in range(3):
    display.tick()
display.sprites.empty()

