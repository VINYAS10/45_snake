import pygame

from game.game_engine import GameEngine


# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 600

SCREEN = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Snake - Pygame Version"
)

# Clock
clock = pygame.time.Clock()
FPS = 60


def main():
    engine = GameEngine(WIDTH, HEIGHT)

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                engine.handle_keydown(event.key)

        engine.handle_input()
        engine.update()
        engine.render(SCREEN)

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()