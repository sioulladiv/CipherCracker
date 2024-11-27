
import itertools
from cipher_utils import bigram_fitness
import argparse
from config import *

class ShuffleCracker:
    def __init__(self):
        self.progress_callback = None

    def update_progress(self, message):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message)

    def apply_permutation(self, text, perm):
        """Apply a permutation key to decode text"""
        result = ""
        perm_len = len(perm)
        
        # Process text in blocks
        for i in range(0, len(text), perm_len):
            block = text[i:i + perm_len]
            if len(block) < perm_len:  # Handle last incomplete block
                result += block
                break
                
            # Create mapping of current positions to original positions
            inverse_perm = [0] * perm_len
            for pos, val in enumerate(perm):
                inverse_perm[val] = pos
                
            # Decode block using inverse permutation
            decoded = [''] * len(block)
            for j, char in enumerate(block):
                decoded[inverse_perm[j]] = char
            result += ''.join(decoded)
            
        return result

    def try_all_permutations(self, ciphertext, length):
        """Try all possible permutations of given length"""
        best_score = float('inf')
        best_perm = None
        best_plain = None
        
        total_perms = factorial(length)
        tried = 0
        
        for perm in itertools.permutations(range(length)):
            tried += 1
            if tried % 1000 == 0:
                self.update_progress(f"Tried {tried}/{total_perms} permutations...")
                
            plaintext = self.apply_permutation(ciphertext, perm)
            score = bigram_fitness(plaintext)
            
            if score < best_score:
                best_score = score
                best_perm = perm
                best_plain = plaintext
                self.update_progress(f"Found better permutation: {perm} (score: {score:.4f})")
        
        return best_plain, best_perm, best_score

    def decrypt(self, ciphertext, forced_length=None):
        self.update_progress("Preprocessing input text...")
        ciphertext = ''.join(c.upper() for c in ciphertext if c.isalpha())
        if not ciphertext:
            raise ValueError("No valid characters in input text")
        
        if forced_length:
            key_length = forced_length
        else:
            # Try lengths within configured bounds
            best_score = float('inf')
            best_length = None
            best_plain = None
            best_perm = None
            
            for length in range(MIN_KEY_LENGTH, MAX_KEY_LENGTH + 1):
                self.update_progress(f"Trying key length {length}...")
                plaintext, perm, score = self.try_all_permutations(ciphertext, length)
                
                if score < best_score:
                    best_score = score
                    best_length = length
                    best_plain = plaintext
                    best_perm = perm
                    if best_score< 0.4:
                        break
            
            return best_plain, best_perm, best_score
            
        self.update_progress(f"Using key length: {key_length}")
        return self.try_all_permutations(ciphertext, key_length)

def factorial(n):
    """Calculate factorial of n"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    parser = argparse.ArgumentParser(description='Shuffle Transposition Cipher Decoder')
    parser.add_argument('-1', '--length', type=int, help='Specify the key length')
    args = parser.parse_args()

    cracker = ShuffleCracker()
    with open('ciphertext.txt', 'r') as f:
        ciphertext = f.read()
    
    if args.length:
        print(f"Using specified key length: {args.length}")
        plaintext, key, score = cracker.decrypt(ciphertext, forced_length=args.length)
    else:
        print("Trying all possible key lengths...")
        plaintext, key, score = cracker.decrypt(ciphertext)
    
    print(f"\nFinal Results:")
    print(f"Key: {key}")
    print(f"Score: {score:.4f}")
    print(f"Decrypted text: {plaintext[:100]}...")

if __name__ == "__main__":
    main()