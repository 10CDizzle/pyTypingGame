import pygame
import random
import math

class Turret:
    def __init__(self):
        self.position = [50, 300]  # Fixed position on the left
        self.exploded = False
        self.explosion_timer = 0
        self.fragments = []
        self.fragment_speed = 3
        self.font = pygame.font.Font(None, 36)

    def explode(self):
        if not self.exploded:
            self.exploded = True
            self.explosion_timer = 60  # Explosion duration

            # Generate fragments (random letters)
            for _ in range(10):  # Create 10 fragments
                letter = chr(random.randint(65, 90))  # Random uppercase letter
                angle = random.uniform(0, 2 * math.pi)
                velocity = [math.cos(angle) * self.fragment_speed, math.sin(angle) * self.fragment_speed]
                self.fragments.append({'letter': letter, 'position': list(self.position), 'velocity': velocity})

    def update(self):
        if self.exploded:
            for fragment in self.fragments:
                fragment['position'][0] += fragment['velocity'][0]
                fragment['position'][1] += fragment['velocity'][1]

            if self.explosion_timer > 0:
                self.explosion_timer -= 1

    def is_finished(self):
        return self.exploded and self.explosion_timer <= 0

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.rect(screen, (0, 255, 0), (self.position[0], self.position[1], 20, 20))
        else:
            for fragment in self.fragments:
                fragment_surface = self.font.render(fragment['letter'], True, (255, 0, 0))
                screen.blit(fragment_surface, fragment['position'])
