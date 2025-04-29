class Dictionary:
    def __init__(self):
        with open('english-words/words_alpha.txt') as f:
            self.words = [line.strip() for line in f]

    def get_random_word(self):
        import random

        return random.choice(self.words)
