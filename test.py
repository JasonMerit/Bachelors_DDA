import pygame
import random
from multiprocessing import Pool, cpu_count

cpu_count = cpu_count()

# Initialize Pygame
pygame.init()

# Set up the screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Static TV Screen")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Main function for generating static
def generate_static(surface):
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            # Randomly flicker pixels on and off
            if random.random() < 0.01:  # Adjust this probability to control flickering intensity
                color = random.choice([WHITE, BLACK])
            else:
                color = BLACK if random.random() < 0.5 else WHITE  # Simulate noise
            surface.set_at((x, y), color)


if __name__ == "__main__":
    # Create a pool of workers
    with Pool(cpu_count) as p:
        # Main game loop
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Generate static
            p.apply_async(generate_static, args=(screen,))

    # Generate static
    # generate_static(screen)

    # # Update the display
    # pygame.display.flip()

    # # Close the pool
    # p.close()
    # p.join()

# Main game loop
# running = True
# while running:
#     # Handle events
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Generate static
#     generate_static(screen)

#     # Update the display
#     pygame.display.flip()

# # Quit Pygame
# pygame.quit()
