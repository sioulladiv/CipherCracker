import itertools
from cipher_utils import bigram_fitness
import argparse
from config import *

class ShuffleCracker:
    def __init__(self):
        self.progress_callback = None
        self.best_score = float('inf')
        self.best_text = ""
        self.best_key = None
        self.running = True

    def update_progress(self, message):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message)
    
    def stop(self):
        """Stop the cipher cracking process"""
        self.running = False

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

    def try_all_permutations(self, ciphertext, length, queue=None):
        """Try all possible permutations of given length"""
        best_score = float('inf')
        best_perm = None
        best_plain = None
        
        total_perms = factorial(length)
        tried = 0
        last_update = 0
        update_frequency = max(100, total_perms // 100)  # Update at most 100 times
        
        self.best_score = best_score
        self.best_text = ""
        self.best_key = None
        
        for perm in itertools.permutations(range(length)):
            # Check if we should stop
            if not self.running:
                break
                
            tried += 1
            
            # Update progress less frequently for better performance
            if tried - last_update >= update_frequency:
                if queue:
                    # Send progress update through queue for GUI
                    queue.put({
                        'type': 'progress',
                        'score': best_score,
                        'text': best_plain if best_plain else "",
                        'key': str(best_perm) if best_perm else ""
                    })
                last_update = tried
                
            plaintext = self.apply_permutation(ciphertext, perm)
            score = bigram_fitness(plaintext)
            
            if score < best_score:
                best_score = score
                best_perm = perm
                best_plain = plaintext
                self.best_score = best_score
                self.best_text = best_plain
                self.best_key = best_perm
                
                # Send immediate update on improvement
                if queue:
                    queue.put({
                        'type': 'progress',
                        'score': best_score,
                        'text': best_plain[:100],
                        'key': str(best_perm)
                    })
        
        return best_plain, best_perm, best_score

    def decrypt(self, ciphertext, forced_length=None, queue=None):
        # Reset running flag at start
        self.running = True
        
        # Clean input without verbose output
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
                # Check if we should stop
                if not self.running:
                    break
                    
                # No text output, just compute
                plaintext, perm, score = self.try_all_permutations(ciphertext, length, queue)
                
                if score < best_score:
                    best_score = score
                    best_length = length
                    best_plain = plaintext
                    best_perm = perm
                    if best_score < 0.4:
                        break
            
            return best_plain, best_perm, best_score
            
        # No text output, just use the specified key length
        return self.try_all_permutations(ciphertext, key_length, queue)

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