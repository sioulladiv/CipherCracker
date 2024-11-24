import math
import cipher_utils
from cipher_utils import bigram_fitness
import string
import pygame
from pygame.locals import *
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import sys
global running
global RESELECT_COEFF
from display_updater import update_gui
import os
import random


iterations = 1000

def transp_subst_run(cText, cipherOptions):
    global cText_orginial 
    cText_orginial = cText
    global running
    global RESELECT_COEFF
    global screen
    global font
    global fitness_scores
    pygame.init()
    size = (800, 740)
    screen = pygame.display.set_mode(size)
    pygame.font.init() 
    font = pygame.font.SysFont('Courier', 18)
    pygame.display.set_caption('epic decyphering')
    programIcon = pygame.image.load('icon.png')
    pygame.display.set_icon(programIcon)
    fitness_scores = []
        
    cText = cipher_utils.clean_text(cText)
    if cipherOptions == 'substitution':
        cipher_sub = SubstitutionCipher()
        result = monte_carlo_cipher(cipher_sub, cText) 
        return result 
    elif cipherOptions == 'transposition':
        cipher_trans = TranspositionCipher()
        result = monte_carlo_cipher(cipher_trans, cText)  
        return result  



class SubstitutionCipher:
    def __init__(self, key=None):
        if key is None:
            self.key = self.generate_key()
        else:
            self.key = key
        self.inverse_key = {v: k for k, v in self.key.items()}

    def generate_key(self):
        letters = list(string.ascii_lowercase)
        shuffled = letters[:]
        random.shuffle(shuffled)
        return dict(zip(letters, shuffled))

    def encrypt(self, text):
        return ''.join(self.key.get(char, char) for char in text.lower())

    def decrypt(self, text):
        return ''.join(self.inverse_key.get(char, char) for char in text.lower())

    def mod_key(self):
        letters = list(self.key.keys())
        l1, l2 = random.sample(letters, 2)
        self.key[l1], self.key[l2] = self.key[l2], self.key[l1]
        self.inverse_key = {v: k for k, v in self.key.items()}

class TranspositionCipher:
    def __init__(self, group_size=6, key=None):
        self.group_size = group_size
        if key is None:
            self.key = self.generate_key()
        else:
            self.key = key

    def generate_key(self):
        permutation = list(range(self.group_size))
        random.shuffle(permutation)
        return permutation

    def apply_permutation(self, text):
        text = text.replace(" ", "")
        groups = [text[i:i + self.group_size] for i in range(0, len(text), self.group_size)]
        permuted_groups = []

        for group in groups:
            if len(group) == self.group_size:
                permuted_group = ''.join(group[idx] for idx in self.key)
                permuted_groups.append(permuted_group)
            else:
                permuted_groups.append(group)

        return ''.join(permuted_groups)

    def encrypt(self, text):
        return self.apply_permutation(text)

    def decrypt(self, text):
        inverse_key = [0] * len(self.key)
        for i, idx in enumerate(self.key):
            inverse_key[idx] = i
        self.key = inverse_key
        return self.apply_permutation(text)

    def mod_key(self):
        idx1, idx2 = random.sample(range(len(self.key)), 2)
        self.key[idx1], self.key[idx2] = self.key[idx2], self.key[idx1]

def monte_carlo_cipher(cipher, cText, iterations=10000, initial_temp=0.8):
    running = True
    pygame.init()  
    
    best_key = cipher.generate_key()
    current_key = best_key.copy() if isinstance(best_key, dict) else best_key[:]
    cipher.key = best_key.copy() if isinstance(best_key, dict) else best_key[:]
    
    best_text = cipher.decrypt(cText.lower())
    best_score = cipher_utils.bigram_fitness(best_text)
    current_score = best_score
    iteration = 0

    temp = initial_temp
    cooling_rate = initial_temp / iterations
    
    while running and iteration < iterations and best_score>0.4:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    result = {
                        'text': best_text,
                        'key': best_key,
                        'score': best_score,
                        'iterations': iteration
                    }
                    pygame.display.quit()
                    pygame.quit()
                    return result

            cipher.key = current_key.copy() if isinstance(current_key, dict) else current_key[:]
            cipher.mod_key()
            new_key = cipher.key.copy() if isinstance(cipher.key, dict) else cipher.key[:]
            
            current_text = cipher.decrypt(cText.lower())
            current_score = cipher_utils.bigram_fitness(current_text)
            
            if current_score < best_score: 
                best_text = cipher.decrypt(cText.lower())
                best_key = new_key.copy() if isinstance(new_key, dict) else new_key[:]
                best_score = current_score
                current_key = new_key.copy() if isinstance(new_key, dict) else new_key[:]
            else:
                delta = current_score - best_score
                probability = math.exp(-delta / temp)
                if random.random() < probability:
                    current_key = new_key.copy() if isinstance(new_key, dict) else new_key[:]
                else:
                    current_key = best_key.copy() if isinstance(best_key, dict) else best_key[:]
            
            temp = max(0.01, temp - cooling_rate)
            iteration += 1
            
            cipher.key = best_key.copy() if isinstance(best_key, dict) else best_key[:]
            
            try:
                gui_result = update_gui(pygame, agg, plt, 300, best_key, current_key,
                                      iteration, round(current_score, 4),
                                      round(best_score, 4), current_text[0:50],
                                      best_text, screen, font, fitness_scores)
                if isinstance(gui_result, dict):  
                    return {
                        'text': gui_result['text'],
                        'key': "".join(list(gui_result['key'].values())) if isinstance(gui_result['key'], dict) else "".join(map(str, gui_result['key'])),
                        'score': gui_result['score'],
                        'iterations': gui_result['iterations']
                    }
            except pygame.error:
                pass  
                
        except pygame.error:
            break  

    result = {
        'text': best_text,
        'key': "".join(best_key.values()) if isinstance(best_key, dict) else "".join(map(str, best_key)),
        'score': best_score,
        'iterations': iteration
    }
    try:
        pygame.display.quit()
        pygame.quit()
    except:
        pass
    return result
