import string
import random
import math
from cipher_utils import bigram_fitness
from config import *
import time
from multiprocessing import Value, Array
import ctypes

class PlayfairCracker:
    def __init__(self):
        self.running = True
        self.LETTERS = string.ascii_uppercase.replace('J', '')  # Remove J for Playfair
        self.progress_callback = None
        self.temperature = INITIAL_TEMPERATURE
        self.cooling_rate = COOLING_RATE
        self.iterations = MAX_ITERATIONS
        self.start_time = None
        self.best_score = float('inf')
        self.best_text = ""
        self.best_key = ""
        self.shared_score = Value(ctypes.c_double, float('inf'))
        self.shared_text = Array(ctypes.c_char, 1000)
        self.shared_key = Array(ctypes.c_char, 26)

    def create_key_matrix(self, key):
        """Convert key string to 5x5 matrix"""
        matrix = []
        used = set()
        # First fill with key letters
        for c in key:
            if c not in used and c in self.LETTERS:
                used.add(c)
        # Then add remaining alphabet
        for c in self.LETTERS:
            if c not in used:
                used.add(c)
        # Create 5x5 matrix
        matrix = list(used)
        return [matrix[i:i+5] for i in range(0, 25, 5)]

    def find_position(self, matrix, char):
        """Find letter position in matrix"""
        if char == 'J': char = 'I'
        for i in range(5):
            for j in range(5):
                if matrix[i][j] == char:
                    return i, j
        # Return default position if character not found
        return 0, 0  # Changed from None to avoid division by zero

    def decrypt_pair(self, matrix, pair):
        """Decrypt a pair of characters using Playfair rules"""
        try:
            row1, col1 = self.find_position(matrix, pair[0])
            row2, col2 = self.find_position(matrix, pair[1])

            if row1 == row2:  # Same row
                return (matrix[row1][(col1-1)%5] + 
                       matrix[row2][(col2-1)%5])
            elif col1 == col2:  # Same column
                return (matrix[(row1-1)%5][col1] + 
                       matrix[(row2-1)%5][col2])
            else:  # Rectangle
                return (matrix[row1][col2] + 
                       matrix[row2][col1])
        except Exception as e:
            print(f"Error decrypting pair {pair}: {str(e)}")
            return 'XX'  # Return placeholder on error

    def decrypt_with_key(self, ciphertext, key):
        """Decrypt entire text using key"""
        try:
            matrix = self.create_key_matrix(key)
            result = []
            
            # Pre-process ciphertext to ensure valid pairs
            processed_text = []
            i = 0
            while i < len(ciphertext):
                if i + 1 >= len(ciphertext):
                    processed_text.append(ciphertext[i] + 'X')
                    i += 1
                else:
                    if ciphertext[i] == ciphertext[i + 1]:
                        processed_text.append(ciphertext[i] + 'X')
                        i += 1
                    else:
                        processed_text.append(ciphertext[i:i+2])
                        i += 2
            
            # Decrypt each valid pair
            for pair in processed_text:
                try:
                    if len(pair) == 2 and pair[0].isalpha() and pair[1].isalpha():
                        decrypted_pair = self.decrypt_pair(matrix, pair)
                        result.append(decrypted_pair)
                    else:
                        result.append('XX')  # Invalid pair placeholder
                except Exception as e:
                    print(f"Error processing pair {pair}: {str(e)}")
                    result.append('XX')
                    
            return ''.join(result)
            
        except Exception as e:
            print(f"Error in decrypt_with_key: {str(e)}")
            return 'X' * len(ciphertext)  # Return placeholder text of same length

    def create_random_key(self):
        """Generate random initial key"""
        key = list(self.LETTERS)
        random.shuffle(key)
        return ''.join(key)

    def swap_letters(self, key):
        """Create new key by swapping two random positions"""
        pos1, pos2 = random.sample(range(25), 2)
        key_list = list(key)
        key_list[pos1], key_list[pos2] = key_list[pos2], key_list[pos1]
        return ''.join(key_list)

    def monte_carlo_optimization(self, ciphertext):
        """Optimize key using Monte Carlo with simulated annealing"""
        self.start_time = time.time()
        current_key = self.create_random_key()
        current_score = bigram_fitness(self.decrypt_with_key(ciphertext, current_key))
        self.best_key = current_key
        self.best_score = current_score
        temp = self.temperature

        for i in range(self.iterations):
            if not self.running:
                break

            if i % 100 == 0:
                self.update_progress(f"Iteration {i}/{self.iterations}")

            new_key = self.swap_letters(current_key)
            new_text = self.decrypt_with_key(ciphertext, new_key)
            new_score = bigram_fitness(new_text)

            delta = new_score - current_score
            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_key = new_key
                current_score = new_score
                
                if current_score < self.best_score:
                    self.best_score = current_score
                    self.best_key = current_key
                    self.best_text = new_text
                    
                    self.shared_score.value = current_score
                    self.shared_text.value = self.best_text[:1000].encode()
                    self.shared_key.value = current_key[:25].encode()

            temp *= self.cooling_rate

        return self.best_key, self.best_score, self.best_text

    def stop(self):
        self.running = False

    def update_progress(self, message):
        if self.progress_callback:
            self.progress_callback(message)

    def decrypt(self, ciphertext, initial_key=None):
        """Main decryption method"""
        try:
            self.update_progress("Preprocessing input text...")
            # Clean input text
            ciphertext = ''.join(c.upper() for c in ciphertext if c.isalpha())
            if not ciphertext:
                raise ValueError("No valid characters in input text")
            
            # Use initial key if provided, otherwise start random
            if initial_key:
                current_key = ''.join(c.upper() for c in initial_key if c.isalpha())
                if len(current_key) < 25:
                    current_key = self.create_random_key()
            else:
                current_key = self.create_random_key()

            self.update_progress("Starting Monte Carlo optimization...")
            key, score, plaintext = self.monte_carlo_optimization(ciphertext)
            
            if not plaintext or score == float('inf'):
                raise ValueError("Failed to find valid solution")

            return plaintext, key, score
            
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            raise