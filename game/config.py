class Config:
    grace_add = 15
    grace_multiply = 0.7

    caption = "Endless Runner"

    width, height = 800, 600
    # WIDTH = 2000
    # HEIGHT = 1000
    BLACK, WHITE, GREY = (30, 30, 30), (255, 255, 255), (179, 178, 194)
    BLUE, GREEN = (100, 100, 255), (100, 200, 100) 
    RED, YELLOW,  = (232, 65, 24), (255, 205, 9)
    COLOR_KEY, SHADE = (255, 0, 255), (255, 255, 255, 100)

    DEBUG = 0
    PLAY = 0

    UNIT = 0.25 # Length of a unit in seconds (minimum distance)
    DENSITY = 10 # Number of hatches
    DURATION = 5 # Length of rhythm in seconds (5, 10, 15, 20)

    FPS: int = 60# 60 # Frames per second (too high, and tapping wlil cross frames)
    # DT = 1 / FPS
    GOD = 0
    AGENT = 1
    FLAT = 0
    TOUCHING = 0
    GAME = 0
    VERBOSE = 0

    # Rune
    delay_id = 1

