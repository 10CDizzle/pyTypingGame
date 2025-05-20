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
        self.score = score

    def update(self, typed_letter):
        self.counter += 1
        if self.counter >= self.spawn_interval:
            self.counter = 0
            self.spawn_word()

        for word in self.words[:]:  # Copy list to safely remove words
            word.update(typed_letter)

            if word.is_finished():  
                self.score.increase_score(len(word.text))  # Increase score based on word length
                self.words.remove(word)  # Remove completed word

        # Check for missed words
        for word in self.words[:]:
            if word.position[0] < 0: # Word moved off screen to the left
                # Check if the word was already exploded (e.g. by a projectile)
                # If not, then it's a missed word.
                # This check might need refinement if words can be "missed" after being typed.
                # For now, assume if it's off-screen and not exploded, it's missed.
                if not word.exploded:
                    self.words.remove(word)
                    self.missed_words += 1
                    if self.missed_words >= self.max_missed_words:
                        self.turret.explode() # Game over condition
    
    def spawn_word(self):
        text = self.dictionary.get_random_word()
        if len(text) <= self.max_word_length:
            x = 800  # Start at the right edge of the screen
            y = random.randint(50, 550)  # Random y position
            self.words.append(Word(text, [x, y], self.turret))
        else:
            # If word is too long, try spawning another one immediately
            # This could lead to a deep recursion if dictionary often returns long words
            # Consider a limit or different strategy if this is an issue
            self.spawn_word()

    def draw(self, screen):
        for word in self.words:
            word.draw(screen)

class Word:
    def __init__(self, text, position, turret):
        self.text = text
        self.position = position  # Top-left position of the word text
        self.speed = 2  # Word movement speed
        self.font = pygame.font.Font(None, 36)
        self.width, self.height = self.font.size(text)
        self.typed_letters = ""
        self.exploded = False
        self.explosion_timer = 0  # Timer for main explosion visual
        self.turret = turret

        # Projectile attributes for curved trajectory
        self.projectile_launched = False
        self.projectile_start_pos = None     # Turret's center position
        self.projectile_target_pos = None    # Word's center position when fully typed (fixed target)
        self.projectile_current_pos = None   # Current position of the projectile
        self.projectile_radius = 8           # Visual radius of the projectile
        self.projectile_t = 0.0              # Parameter for Bezier curve (0.0 to 1.0)
        
        # Defines how many game frames the projectile takes to reach its target.
        # Lower value means faster projectile.
        self.projectile_flight_frames = 30 
        self.projectile_dt = 1.0 / self.projectile_flight_frames if self.projectile_flight_frames > 0 else 1.0

        # Bezier curve control point offsets (relative to midpoint of start and target)
        # A negative Y offset creates an upward arc (assuming Y increases downwards).
        self.projectile_control_point_y_offset = -80  # pixels, for upward arc
        self.projectile_control_point_x_offset = 0    # pixels, for horizontal skew of arc

        # Fragmentation attributes
        self.fragments = []
        self.fragment_speed = 3 # Speed of individual letter fragments

    def update(self, typed_letter):
        if not self.exploded:
            # Word movement
            self.position[0] -= self.speed

            # Typing logic
            if typed_letter and not self.is_fully_typed():
                # Check if the typed letter is the next correct letter
                if len(self.typed_letters) < len(self.text) and \
                   self.text[len(self.typed_letters)] == typed_letter:
                    self.typed_letters += typed_letter

            # Projectile logic: if word is fully typed, manage projectile
            if self.is_fully_typed():
                if not self.projectile_launched:
                    # First frame the word is fully typed: initialize and launch projectile
                    self.projectile_launched = True
                    
                    # Start projectile from turret's center
                    # Assuming turret rect is (turret.position[0], turret.position[1], 20, 20)
                    turret_center_x = self.turret.position[0] + 10 
                    turret_center_y = self.turret.position[1] + 10
                    self.projectile_start_pos = [turret_center_x, turret_center_y]
                    
                    # Target the word's visual center at the moment of launch
                    word_center_x = self.position[0] + self.width / 2
                    word_center_y = self.position[1] + self.height / 2
                    self.projectile_target_pos = [word_center_x, word_center_y]
                    
                    self.projectile_current_pos = list(self.projectile_start_pos)
                    self.projectile_t = 0.0
                
                self._update_projectile_flight() # Update projectile position along curve
        
        else: # if self.exploded
            # Update fragments
            for fragment in self.fragments[:]: # Iterate on a copy for safe removal
                fragment['position'][0] += fragment['velocity'][0]
                fragment['position'][1] += fragment['velocity'][1]
                fragment['lifetime'] -= 1
                if fragment['lifetime'] <= 0:
                    self.fragments.remove(fragment)

            # Decrease main explosion timer
            if self.explosion_timer > 0:
                self.explosion_timer -= 1

    def _update_projectile_flight(self):
        """Updates the projectile's position along a quadratic Bezier curve."""
        if not self.exploded and self.projectile_launched and self.projectile_t < 1.0:
            self.projectile_t += self.projectile_dt
            self.projectile_t = min(self.projectile_t, 1.0) # Cap at 1.0

            P0 = self.projectile_start_pos
            P2 = self.projectile_target_pos # The fixed destination

            # Calculate control point P1 for the quadratic Bezier curve
            # Midpoint between P0 (start) and P2 (target)
            mid_x = (P0[0] + P2[0]) / 2
            mid_y = (P0[1] + P2[1]) / 2
            
            # Apply offsets to the midpoint to define the curve's shape
            P1_x = mid_x + self.projectile_control_point_x_offset
            P1_y = mid_y + self.projectile_control_point_y_offset
            
            # Quadratic Bezier formula: B(t) = (1-t)^2*P0 + 2*(1-t)*t*P1 + t^2*P2
            t = self.projectile_t
            one_minus_t = 1.0 - t
            
            current_x = (one_minus_t**2 * P0[0] +
                         2 * one_minus_t * t * P1_x +
                         t**2 * P2[0])
            current_y = (one_minus_t**2 * P0[1] +
                         2 * one_minus_t * t * P1_y +
                         t**2 * P2[1])
            self.projectile_current_pos = [current_x, current_y]

            # If projectile reaches its target destination (end of the curve)
            if self.projectile_t >= 1.0:
                self.explode() # Trigger the word's explosion

    def is_fully_typed(self):
        return self.typed_letters == self.text

    def explode(self):
        if not self.exploded: # Ensure explosion happens only once
            self.exploded = True
            self.explosion_timer = 30  # Duration of the main explosion visual (e.g., a flash)

            # Create letter fragments at the word's current center position
            explode_center_x = self.position[0] + self.width / 2
            explode_center_y = self.position[1] + self.height / 2

            for letter_char in self.text:
                angle = random.uniform(0, 2 * math.pi) # Random direction for each fragment
                velocity = [math.cos(angle) * self.fragment_speed, 
                            math.sin(angle) * self.fragment_speed]
                self.fragments.append({
                    'letter': letter_char,
                    'position': [explode_center_x, explode_center_y], # Start from word's center
                    'velocity': velocity,
                    'lifetime': random.randint(20, 40) # Frames for fragment to live
                })

    def is_finished(self):
        """Word is considered finished (and can be removed) when it has exploded, 
           its main explosion animation is done, and all its fragments are gone."""
        return self.exploded and self.explosion_timer <= 0 and not self.fragments

    def draw(self, screen):
        if not self.exploded:
            # Draw the word text (untyped part)
            word_surface = self.font.render(self.text, True, (255, 255, 255)) # White
            screen.blit(word_surface, self.position)
            
            # Draw the typed part of the word in a different color (e.g., green)
            if self.typed_letters:
                typed_surface = self.font.render(self.typed_letters, True, (0, 255, 0)) # Green
                screen.blit(typed_surface, self.position) # Overlay on top of the white text

            # Draw the projectile if it has been launched and is still in flight
            if self.projectile_launched and self.projectile_current_pos and self.projectile_t < 1.0:
                pygame.draw.circle(screen, (255, 0, 0),  # Red projectile
                                   (int(self.projectile_current_pos[0]), int(self.projectile_current_pos[1])), 
                                   self.projectile_radius)
        else: # If exploded, draw fragments
            for fragment in self.fragments:
                fragment_surface = self.font.render(fragment['letter'], True, (255, 165, 0)) # Orange fragments
                screen.blit(fragment_surface, fragment['position'])
