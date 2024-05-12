import pygame as pg

# A subset of these are used in different contexts
# {action: [triggers]}
key_actions = {
    "quit":             (pg.KEYDOWN, [pg.K_ESCAPE]),
    "jump":             (pg.KEYDOWN, [pg.K_SPACE, pg.K_UP, pg.K_w]),
    "jump_release":     (pg.KEYUP, [pg.K_SPACE, pg.K_UP, pg.K_w]),
    "pause":            (pg.KEYDOWN, [pg.K_p]),
    "reset":            (pg.KEYDOWN, [pg.K_r]), 
    "increase_speed":   (pg.KEYDOWN, [pg.K_RIGHT, pg.K_d]),
    "decrease_speed":   (pg.KEYDOWN, [pg.K_LEFT, pg.K_a]),
    "increase_difficulty": (pg.KEYDOWN, [pg.K_e]),
    "decrease_difficulty": (pg.KEYDOWN, [pg.K_q]),
    "render":           (pg.KEYDOWN, [pg.K_v]),
}