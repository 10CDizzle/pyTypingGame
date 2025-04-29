import pygame

class Score:
    def __init__(self):
        self.score = 0

    def increase_score(self, points):
        self.score += points

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        score_surface = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_surface, (10, 10))
