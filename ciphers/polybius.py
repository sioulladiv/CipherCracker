import itertools
from cipher_utils import bigram_fitness  # Changed from relative to absolute import
from config import *  # Changed from relative to absolute import

class PolybiusCracker:
    def __init__(self):
        self.progress_callback = None
        self.ALPHABET = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # Note: I/J are combined

    def update_progress(self, message):
        if self.progress_callback:
            self.progress_callback(message)

    def create_square(self, key):
        """Create 5x5 Polybius square from key"""
        # Remove duplicates while preserving order
        key = ''.join(dict.fromkeys(key.upper() + self.ALPHABET))
        return [key[i:i+5] for i in range(0, 25, 5)]

    def decode_text(self, ciphertext, square):
        """Decode text using Polybius square"""
        result = ""
        coords = []
        
        # Convert numbers to coordinates
        for i in range(0, len(ciphertext), 2):
            if i+1 < len(ciphertext):
                row = int(ciphertext[i]) - 1
                col = int(ciphertext[i+1]) - 1
                if 0 <= row < 5 and 0 <= col < 5:
                    coords.append((row, col))

        # Convert coordinates to letters
        for row, col in coords:
            result += square[row][col]
            
        return result

    def evaluate_key(self, ciphertext, key):
        """Evaluate a potential key"""
        square = self.create_square(key)
        plaintext = self.decode_text(ciphertext, square)
        return bigram_fitness(plaintext), plaintext

    def decrypt(self, ciphertext, initial_key=None):
        """Main decryption method"""
        self.update_progress("Starting Polybius cipher decryption...")
        
        # Clean input - keep only digits
        ciphertext = ''.join(c for c in ciphertext if c.isdigit())
        if len(ciphertext) % 2 != 0:
            raise ValueError("Invalid Polybius cipher text length (must be even)")

        best_score = float('inf')
        best_key = None
        best_plain = None
        
        # Try random keys or start with initial key
        test_keys = [''] if not initial_key else [initial_key]
        
        for key in test_keys:
            score, plaintext = self.evaluate_key(ciphertext, key)
            if score < best_score:
                best_score = score
                best_key = key
                best_plain = plaintext
                self.update_progress(f"Found better key: {key} (score: {score:.4f})")

        if best_plain:
            return best_plain, best_key, best_score
        raise ValueError("Failed to decrypt Polybius cipher")