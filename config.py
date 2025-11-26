"""General configuration settings for decoder"""

cipher_type = 'vigenere'

"""Configuration settings for Vigenere cipher decoder"""

# Key length detection settings
MIN_KEY_LENGTH = 4
MAX_KEY_LENGTH = 7
MIN_SEQUENCE_LENGTH = 3
MAX_SEQUENCE_LENGTH = 7
MIN_REPETITIONS = 3

# Statistical analysis settings
EXPECTED_IOC = 1.73
TARGET_FITNESS = 0.4
MAX_ITERATIONS = 100000

# English letter frequencies (percentages)
ENGLISH_FREQS = {
    'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,
    'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3
}

# Program settings
DEFAULT_INPUT_FILE = 'ciphertext.txt'
SHOW_PROGRESS = True
USE_PARALLEL = True
MAX_WORKERS = 4

# Algorithm settings
COOLING_RATE = 0.003
INITIAL_TEMPERATURE = 2.0

# Shuffle cipher settings
MIN_SHUFFLE_GROUP = 2
MAX_SHUFFLE_GROUP = 8

# Polybius cipher settings
POLYBIUS_CHARSET = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # I/J combined
POLYBIUS_SIZE = 5  # 5x5 grid

"""Playfair cipher settings"""
PLAYFAIR_IGNORE_J = True  # Replace J with I
PLAYFAIR_PAD_CHAR = 'X'  # Character used for padding odd-length text