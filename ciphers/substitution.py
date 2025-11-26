import string
import random
import math
from collections import Counter
from cipher_utils import bigram_fitness  # Use absolute import
from config import *  # Use absolute import
import time
from multiprocessing import Value, Array
import argparse
import ctypes

def run_substitution_process(cipher_text, queue=None):
    """Standalone function to run substitution decoding in a separate process"""
    try:
        cracker = SubstitutionCracker()
        cracker.queue = queue
        plaintext, key, score = cracker.decrypt(cipher_text)
        
        # Ensure we clean up shared memory
        cracker._cleanup_shared_memory()
        
        return {
            'plaintext': plaintext,
            'key': key,
            'score': score,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

class SubstitutionCracker:
    def __init__(self):
        self.running = True
        self.LETTERS = string.ascii_uppercase
        self.progress_callback = None
        self.temperature = 10.0
        self.cooling_rate = 0.95
        self.iterations = 10000
        self.start_time = None
        self.best_score = float('inf')
        self.best_text = ""
        self.best_key = ""
        self.queue = None
        self._init_shared_memory()

    def _init_shared_memory(self):
        try:
            self.shared_score = Value(ctypes.c_double, float('inf'))
            self.shared_text = Array(ctypes.c_char, 1000)
            self.shared_key = Array(ctypes.c_char, 27)
        except Exception as e:
            print(f"Warning: Could not initialize shared memory: {e}")
            self.shared_score = None
            self.shared_text = None
            self.shared_key = None

    def _cleanup_shared_memory(self):
        try:
            if hasattr(self, 'shared_score'):
                self.shared_score = None
            if hasattr(self, 'shared_text'):
                self.shared_text = None
            if hasattr(self, 'shared_key'):
                self.shared_key = None
        except:
            pass

    def update_progress(self, message):
        "update"
        if self.progress_callback:
            self.progress_callback(message)

    def create_random_key(self):
        english_freq = list("ETAOINSHRDLCUMWFGYPBVKJXQZ")
        
        freq_count = Counter(self.ciphertext)
        
        cipher_freq = sorted(set(self.LETTERS), 
                           key=lambda x: freq_count.get(x, 0),
                           reverse=True)
        
        key_dict = {}
        for i in range(len(self.LETTERS)):
            if i < len(cipher_freq):
                key_dict[cipher_freq[i]] = english_freq[i]
            else:
                # Handle any missing letters
                unused = [c for c in english_freq if c not in key_dict.values()]
                unmapped = [c for c in self.LETTERS if c not in key_dict.keys()]
                for c, e in zip(unmapped, unused):
                    key_dict[c] = e
        
        key = ''.join(key_dict[c] for c in self.LETTERS)
        return key

    def swap_letters(self, key):
        """Create new key by swapping two random positions"""
        pos1, pos2 = random.sample(range(26), 2)
        key_list = list(key)
        key_list[pos1], key_list[pos2] = key_list[pos2], key_list[pos1]
        return ''.join(key_list)

    def decrypt_with_key(self, ciphertext, key):
        """Decrypt text using substitution key"""
        trans = str.maketrans(self.LETTERS, key)
        return ciphertext.translate(trans)
    
    def stop(self):
        self.running = False
    
    def updateMssg(self):
        """Return current best metrics and elapsed time"""
        current_time = time.time() - (self.start_time or time.time())
        return {
            'time': f"{current_time:.1f}s",
            'best_score': self.shared_score.value,
            'best_text': self.shared_text.value.decode(),
            'best_key': self.shared_key.value.decode()
        }

    def monte_carlo_optimization(self, ciphertext: str) -> tuple[str, float]:
        self.ciphertext = ciphertext
        self.start_time = time.time()
        current_key = self.create_random_key()
        current_score = bigram_fitness(self.decrypt_with_key(ciphertext, current_key))
        best_key = current_key
        best_score = current_score
        best_text = self.decrypt_with_key(ciphertext, current_key)
        temp = self.temperature
        
        # Update frequency control
        update_interval = max(500, self.iterations // 20)  # Update at most 20 times

        for i in range(self.iterations):
            # Only update progress every update_interval iterations
            if i % update_interval == 0:
                if self.queue:
                    self.queue.put({
                        'type': 'progress',
                        'score': best_score,
                        'text': best_text[:100],  # Limit text length
                        'key': best_key
                    })

            # Create neighbor solution
            new_key = self.swap_letters(current_key)
            new_text = self.decrypt_with_key(ciphertext, new_key)
            new_score = bigram_fitness(new_text)

            # Calculate acceptance probability
            delta = new_score - current_score
            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_key = new_key
                current_score = new_score
                if current_score < best_score:
                    best_score = current_score
                    best_key = current_key
                    best_text = new_text
                    # Update shared memory
                    if self.shared_score:
                        self.shared_score.value = current_score
                        self.shared_text.value = best_text[:1000].encode()
                        self.shared_key.value = current_key.encode()
            temp *= self.cooling_rate

        # Store best results in instance for compatibility
        self.best_key = best_key
        self.best_score = best_score
        self.best_text = best_text
        return best_key, best_score

    def decrypt(self, ciphertext: str) -> tuple[str, str, float]:
        """Main decryption method"""
        ciphertext = ''.join(c.upper() for c in ciphertext if c.isalpha())
        if not ciphertext:
            raise ValueError("No valid characters in input text")

        key, score = self.monte_carlo_optimization(ciphertext)
        plaintext = self.decrypt_with_key(ciphertext, key)
        logging.info(f"Decryption complete. Best score: {score:.4f}")
        return plaintext, key, score
