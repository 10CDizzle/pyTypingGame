import pygame
from turret import Turret
from words import WordManager
from score import Score
from dictionary import Dictionary

# Initialize Pygame and other elements
pygame.init()

# Game setup
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create instances of the game elements
turret = Turret()
score = Score()
word_manager = WordManager(Dictionary(), turret, score, max_word_length=6)

# Game loop
running = True
game_over = False
typed_letter = None

while running:
    typed_letter = None  # Reset typed letter each frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            typed_letter = event.unicode.lower()

    if not game_over:
        # Update game elements
        word_manager.update(typed_letter)
        turret.update()

        # If the turret exploded and finished its animation, end the game
        if turret.is_finished():
            game_over = True

    # Render the screen
    screen.fill((0, 0, 0))

    if not game_over:
        word_manager.draw(screen)
        turret.draw(screen)
        score.draw(screen)
    else:
        # Display game over screen
        font = pygame.font.Font(None, 48)
        text_surface = font.render(
            f"Game Over! Score: {score.score}", True, (255, 255, 255)
        )
        screen.blit(text_surface, (300, 250))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
