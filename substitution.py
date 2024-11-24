import string
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from cipher_utils import bigram_fitness
import argparse
from config import *
from typing import Dict, Optional
import random
import string
import random
from collections import Counter

class SubstitutionCracker:
    def __init__(self):
        self.LETTERS = string.ascii_uppercase
        self.COMMON_WORDS = {'THE', 'BE', 'TO', 'OF', 'AND', 'IN', 'THAT', 'IS'}
        self.COMMON_PATTERNS = {
            'TH', 'HE', 'AN', 'IN', 'ER', 'ON', 'RE', 'ED', 'ND', 'HA', 'AT', 'EN', 'ES', 'OF', 'NT', 'EA', 'TI', 'TO', 'IO', 'LE', 'IS', 'OU', 'AR', 'AS', 'DE', 'RT', 'VE'
        }
    def get_initial_mapping(self, freq) -> dict:
        """Generate initial random mapping for substitution cipher.
        
        Args:
            freq: Counter object with letter frequencies
            
        Returns:
            dict: Mapping of characters to their substitutions
        """
        # Standard alphabet
        alphabet = string.ascii_uppercase
        
        # Create shuffled version of alphabet
        shuffled = list(alphabet)
        random.shuffle(shuffled)
        
        # Create mapping dictionary
        mapping = {}
        for a, b in zip(alphabet, shuffled):
            mapping[a] = b
            mapping[a.lower()] = b.lower()
        
        return mapping

    def analyze_patterns(self, text):
        """Find repeated patterns and word structures"""
        words = text.split()
        patterns = {}
        
        for word in words:
            # Create pattern like: HELLO -> 12334
            seen = {}
            pattern = ''
            for c in word:
                if c not in seen:
                    seen[c] = str(len(seen) + 1)
                pattern += seen[c]
            patterns[pattern] = patterns.get(pattern, []) + [word]
            
        return patterns

    def score_solution(self, text):
        """Score based on n-grams and word patterns"""
        score = bigram_fitness(text)
        
        # Bonus for common English patterns
        for pattern in self.COMMON_PATTERNS:
            if pattern in text:
                score *= 0.95
                
        # Bonus for common words
        words = text.split()
        for word in words:
            if word in self.COMMON_WORDS:
                score *= 0.9
                
        return score

    def smart_swap(self, key, ciphertext):
        """Make intelligent swaps based on patterns"""
        new_key = key.copy()
        
        # Try swapping letters that appear in similar positions
        pos_freq = defaultdict(Counter)
        for i, c in enumerate(ciphertext):
            pos_freq[i % 3][c] += 1
            
        # Find letters that might be related
        related = []
        for pos in pos_freq:
            common = pos_freq[pos].most_common(3)
            related.extend([pair[0] for pair in common])
            
        if related:
            c1, c2 = random.sample(related, 2)
            new_key[c1], new_key[c2] = new_key[c2], new_key[c1]
            
        return new_key

    def decrypt(self, ciphertext):
        """Main solving method"""
        text = ''.join(c for c in ciphertext.upper() if c.isalpha())
        patterns = self.analyze_patterns(text)
        
        # Initial key based on frequency analysis
        freq = Counter(text)
        initial_key = self.get_initial_mapping(freq)
        
        best_key = initial_key
        best_score = float('inf')
        temperature = 2.0
        
        for iteration in range(10000):
            new_key = self.smart_swap(best_key, text)
            plaintext = ''.join(new_key[c] for c in text)
            score = self.score_solution(plaintext)
            
            if score < best_score:
                best_score = score
                best_key = new_key
                print(f"Better solution (score: {score:.4f})")
                print(plaintext[:50])
                
            temperature *= 0.997
            
        return plaintext, best_key, best_score
    
if __name__ == "__main__":
    # Default variables that can be modified directly
    input_file = 'ciphertext.txt'
    cipher_type = 'substitution'

    try:
        with open(input_file, 'r') as f:
            ciphertext = f.read()

        cracker = SubstitutionCracker()
        plaintext, key, score = cracker.decrypt(ciphertext)

        print(f"\nFinal Results:")
        print(f"Key: {key}")
        print(f"Score: {score:.4f}")
        print(f"Decrypted text:\n{plaintext[:200]}...")

    except FileNotFoundError:
        print(f"Error: Could not find file '{input_file}'")
    except Exception as e:
        print(f"Error: {str(e)}")


def create_substitution_map(pattern: str, replacement: str) -> Dict[str, str]:
    """Create a substitution mapping from pattern to replacement."""
    if len(pattern) != len(replacement):
        raise ValueError("Pattern and replacement must be same length")
    return dict(zip(pattern, replacement))

def fast_substitution(text: str, pattern: str, replacement: str) -> str:
    """
    Perform fast substitution using dictionary mapping.
    Similar to decode's technique but for substitution.
    """
    # Create mapping dictionary
    sub_map = create_substitution_map(pattern, replacement)
    
    # Default to original character if no substitution exists
    mapping = defaultdict(lambda: None)
    mapping.update(sub_map)
    
    # Perform substitution using join for efficiency
    return ''.join(mapping[c] or c for c in text)