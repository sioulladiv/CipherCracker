import string
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from cipher_utils import bigram_fitness  # Changed from relative to absolute import
import argparse
from config import *

class VigenereCracker:
    def __init__(self):
        self.LETTERS = string.ascii_uppercase
        self.ENGLISH_FREQS = ENGLISH_FREQS
        self.EXPECTED_IOC = EXPECTED_IOC
        self.progress_callback = None
        self.best_score = float('inf')
        self.best_text = ""
        self.best_key = ""
        self.target_fitness = 0.4  # Add default target fitness

    def update_progress(self, message):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message)


    def calculate_IoC(self, text):
        """Calculate Index of Coincidence"""
        n = len(text)
        if n < 2:
            return 0
        freqs = Counter(text)
        ioc = sum(f * (f-1) for f in freqs.values()) / (n * (n-1))
        return ioc * 26.0

    def find_repeated_sequences(self, text):
        repeats = {}
        for length in range(MIN_SEQUENCE_LENGTH, MAX_SEQUENCE_LENGTH):
            for i in range(len(text) - length):
                seq = text[i:i + length]
                if seq in repeats:
                    repeats[seq].append(i)
                else:
                    repeats[seq] = [i]
        return {k: v for k, v in repeats.items() if len(v) >= MIN_REPETITIONS}

    def determine_key_length(self, ciphertext):
        """Combined key length detection using Kasiski and IoC with config bounds"""
        repeats = self.find_repeated_sequences(ciphertext)
        factors = Counter()
        
        # Get factors within configured range
        for positions in repeats.values():
            spacings = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
            for spacing in spacings:
                for i in range(MIN_KEY_LENGTH, min(spacing, MAX_KEY_LENGTH + 1)):
                    if spacing % i == 0:
                        factors[i] += 1
    
        candidates = []
        # Only consider lengths within configured range
        for length in range(MIN_KEY_LENGTH, MAX_KEY_LENGTH + 1):
            total_ioc = 0
            for i in range(length):
                column = ciphertext[i::length]
                total_ioc += self.calculate_IoC(column)
            avg_ioc = total_ioc / length
            score = abs(avg_ioc - self.EXPECTED_IOC)
            if length in factors:
                score *= 0.5  # Prefer lengths that appear as factors
            candidates.append((length, score))
    
        if not candidates:
            print(f"Warning: No candidates found in range {MIN_KEY_LENGTH}-{MAX_KEY_LENGTH}")
            return MIN_KEY_LENGTH
    
        best_length = min(candidates, key=lambda x: x[1])[0]
        ioc = sum(self.calculate_IoC(ciphertext[i::best_length]) 
                 for i in range(best_length)) / best_length
        
        print(f"Key length found: {best_length} (IoC: {ioc:.3f})")
        return best_length
    
    def try_key_permutations(self, ciphertext, key):
        """Try all cyclic shifts of the key and find best scoring result"""
        best_score = float('inf')
        best_key = key
        best_plain = None
        
        # Try all rotations of the key
        for i in range(len(key)):
            rotated_key = key[i:] + key[:i]
            plaintext = ''
            
            # Decrypt with current key rotation
            for j, c in enumerate(ciphertext):
                shift = ord(rotated_key[j % len(rotated_key)]) - ord('A')
                plaintext += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            
            # Score using bigram fitness
            score = bigram_fitness(plaintext)
            
            # Update if better score found
            if score < best_score:
                best_score = score
                best_key = rotated_key
                best_plain = plaintext
                print(f"Found better key: {best_key} (score: {best_score:.4f})")
        
        if best_plain is None:
            print("Warning: No valid decryption found")
            return ciphertext, key, float('inf')
            
        return best_plain, best_key, best_score

    def find_key_length_by_ioc(self, ciphertext):
        """Fallback IoC method respecting config bounds"""
        best_length = MIN_KEY_LENGTH
        best_ioc = 0
        
        for length in range(MIN_KEY_LENGTH, MAX_KEY_LENGTH + 1):
            total_ioc = 0
            for i in range(length):
                column = ciphertext[i::length]
                total_ioc += self.calculate_IoC(column)
            avg_ioc = total_ioc / length
            
            if best_length == MIN_KEY_LENGTH or abs(avg_ioc - self.EXPECTED_IOC) < abs(best_ioc - self.EXPECTED_IOC):
                best_ioc = avg_ioc
                best_length = length
        
        print(f"Key length found (IoC method): {best_length} (IoC: {best_ioc:.3f})")
        return best_length
    
    def analyze_column(self, column):
        """Frequency analysis with correlation"""
        column = ''.join(c for c in column if c in self.LETTERS)
        if not column:
            return 'A'
            
        column_len = len(column)
        observed_freqs = [0] * 26
        
        for c in column:
            idx = ord(c) - ord('A')
            if 0 <= idx < 26:
                observed_freqs[idx] += 1
        
        observed_freqs = [f * 100 / column_len for f in observed_freqs]
        
        expected_freqs = [0] * 26
        for letter, freq in self.ENGLISH_FREQS.items():
            expected_freqs[ord(letter) - ord('A')] = freq
        
        best_shift = 0
        best_correlation = float('-inf')
        
        for shift in range(26):
            correlation = 0
            shifted_freqs = observed_freqs[shift:] + observed_freqs[:shift]
            
            for obs, exp in zip(shifted_freqs, expected_freqs):
                if exp > 0:
                    correlation += obs * exp
            
            if correlation > best_correlation:
                best_correlation = correlation
                best_shift = shift
        
        return chr(ord('A') + best_shift)

    def decrypt(self, ciphertext, forced_length=None):
        try:
            self.update_progress("Preprocessing input text...")
            ciphertext = ''.join(c.upper() for c in ciphertext if c.isalpha())
            if not ciphertext:
                raise ValueError("No valid characters in input text")
        
            self.update_progress("Determining key length...")
            key_length = forced_length if forced_length else self.determine_key_length(ciphertext)
        
            self.update_progress("Analyzing frequency patterns...")
            with ThreadPoolExecutor() as executor:
                columns = [''.join(ciphertext[i::key_length]) for i in range(key_length)]
                key_chars = list(executor.map(self.analyze_column, columns))
        
            initial_key = ''.join(key_chars)
            self.update_progress(f"Initial key found: {initial_key}")
        
            self.update_progress("Optimizing key...")
            plaintext, key, score = self.try_key_permutations(ciphertext, initial_key)
            self.update_progress(f"Final key found: {key}")
        
            if self.best_score < float('inf'):
                return self.best_text, self.best_key, self.best_score
            return plaintext, key, score
        except Exception as e:
            print(f"Error in Vigenere decrypt: {e}")
            raise
    
def main():
    parser = argparse.ArgumentParser(description='Vigenere Cipher Decoder')
    parser.add_argument('-1', '--length', type=int, help='Specify the key length')
    args = parser.parse_args()

    cracker = VigenereCracker()
    with open('ciphertext.txt', 'r') as f:
        ciphertext = f.read()
    
    if args.length:
        print(f"Using specified key length: {args.length}")
        cracker.key_length = args.length
        plaintext, key, score = cracker.decrypt(ciphertext, forced_length=args.length)
    else:
        print("Attempting to detect key length automatically...")
        plaintext, key, score = cracker.decrypt(ciphertext)
    
    print(f"\nFinal Results:")
    print(f"Key: {key}")
    print(f"Score: {score:.4f}")
    print(f"Decrypted text: {plaintext[:100]}...")

if __name__ == "__main__":
    main()