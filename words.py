import pygame
import random
import math

class WordManager:
    def __init__(self, dictionary, turret, score, max_word_length=6):
        self.words = []
        self.dictionary = dictionary
        self.spawn_interval = 100
        self.counter = 0
        self.turret = turret
        self.missed_words = 0
        self.max_missed_words = 3  # Game over threshold
        self.max_word_length = max_word_length  # Max word length
        self.score = score  # NEW: Score object

    def update(self, typed_letter):
        self.counter += 1
        if self.counter >= self.spawn_interval:
            self.counter = 0
            self.spawn_word()

        for word in self.words[:]:  # Copy list to safely remove words
            word.update(typed_letter)

            if word.is_finished():  
                self.score.add_points(len(word.text))  # Increase score based on word length
                self.words.remove(word)  # Remove completed word

        # Check for missed words
        for word in self.words[:]:
            if word.position[0] < 0:
                self.words.remove(word)
                self.missed_words += 1
                if self.missed_words >= self.max_missed_words:
                    self.turret.explode()
    def spawn_word(self):
        text = self.dictionary.get_random_word()
        if len(text) <= self.max_word_length:
            x = 800  # Start at the right edge of the screen
            y = random.randint(50, 550)  # Random y position
            self.words.append(Word(text, [x, y], self.turret))
        else:
            self.spawn_word()

    def draw(self, screen):
        for word in self.words:
            word.draw(screen)

class Word:
    def __init__(self, text, position, turret):
        self.text = text
        self.position = position
        self.speed = 2  # Adjust this for word speed
        self.font = pygame.font.Font(None, 36)
        self.width, self.height = self.font.size(text)
        self.typed_letters = ""
        self.exploded = False
        self.explosion_timer = 0  # Timer to keep the explosion on screen for a moment
        self.turret = turret

        # Projectile attributes
        self.projectile_position = list(turret.position)
        self.projectile_speed = 5
        self.projectile_radius = 10

        # Fragmentation
        self.fragments = []
        self.fragment_speed = 3

    def update(self, typed_letter):
        if not self.exploded:
            self.position[0] -= self.speed  # Move word across screen

            if typed_letter and not self.is_fully_typed():
                if self.text[len(self.typed_letters)] == typed_letter:
                    self.typed_letters += typed_letter

            if self.is_fully_typed():
                self.launch_projectile()
        else:
            # Update the fragments
            for fragment in self.fragments:
                fragment['position'][0] += fragment['velocity'][0]
                fragment['position'][1] += fragment['velocity'][1]

            # Decrease explosion timer
            if self.explosion_timer > 0:
                self.explosion_timer -= 1

    def launch_projectile(self):
        if not self.exploded:
            dx = self.position[0] - self.projectile_position[0]
            dy = self.position[1] - self.projectile_position[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < self.projectile_speed:  # Projectile reached the word
                self.explode()
                
            else:
                self.projectile_position[0] += (dx / distance) * self.projectile_speed
                self.projectile_position[1] += (dy / distance) * self.projectile_speed

    def is_fully_typed(self):
        return self.typed_letters == self.text

    def explode(self):
        self.exploded = True
        self.explosion_timer = 30  # Explosion lasts for 30 frames

        # Create fragments for each letter
        for letter in self.text:
            angle = random.uniform(0, 2 * math.pi)
            velocity = [math.cos(angle) * self.fragment_speed, math.sin(angle) * self.fragment_speed]
            self.fragments.append({'letter': letter, 'position': list(self.position), 'velocity': velocity})

    def is_finished(self):
        return self.exploded and self.explosion_timer <= 0 and not self.fragments

    def draw(self, screen):
        if not self.exploded:
            # Draw the word and progress
            word_surface = self.font.render(self.text, True, (255, 255, 255))
            typed_surface = self.font.render(self.typed_letters, True, (0, 255, 0))
            
            screen.blit(word_surface, self.position)
            screen.blit(typed_surface, self.position)

            # Draw the projectile
            pygame.draw.circle(screen, (255, 0, 0), (int(self.projectile_position[0]), int(self.projectile_position[1])), self.projectile_radius)
        else:
            # Draw fragments
            for fragment in self.fragments:
                fragment_surface = self.font.render(fragment['letter'], True, (255, 165, 0))
                screen.blit(fragment_surface, fragment['position'])
