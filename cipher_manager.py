from cipher_utils import bigram_fitness
from substitution import SubstitutionCracker
import config

#you are so silly
from vigenere import VigenereCracker
from shuffle import ShuffleCracker
from polybius import PolybiusCracker

class CipherManager:
    def __init__(self):
        self.vigenere_cracker = VigenereCracker()
        self.substitution_cracker = SubstitutionCracker()
        self.shuffle_cracker = ShuffleCracker()
        self.polybius_cracker = PolybiusCracker()

    
    def updateInfoSubstition(self):
        """Get current metrics from substitution cracker"""
        return self.substitution_cracker.updateMssg()
    
    def run_shuffle_decoder(self, cipher_text, group_length=None, progress_callback=None):
            """Handle Vigenere cipher decoding"""
            if progress_callback:
                self.shuffle_cracker.progress_callback = progress_callback
                
            try:
                plaintext, key, score = self.shuffle_cracker.decrypt(cipher_text, group_length)
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

    def run_vigenere_decoder(self, cipher_text, forced_length=None, progress_callback=None):
        """Handle Vigenere cipher decoding"""
        if progress_callback:
            self.vigenere_cracker.progress_callback = progress_callback
            
        try:
            plaintext, key, score = self.vigenere_cracker.decrypt(cipher_text, forced_length)
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

    def run_substitution_decoder(self, cipher_text, forced_length=None, progress_callback=None, queue=None):
        """Handle substitution cipher decoding with process communication"""
        try:
            self.substitution_cracker.progress_callback = progress_callback
            # Pass queue to substitution cracker
            self.substitution_cracker.queue = queue
            plaintext, key, score = self.substitution_cracker.decrypt(cipher_text)
            
            if queue:
                result = {
                    'plaintext': plaintext,
                    'key': key,
                    'score': score,
                    'success': True
                }
                queue.put({'type': 'finished', 'result': result})
            
            return {
                'plaintext': plaintext,
                'key': key,
                'score': score,
                'success': True
            }
        except Exception as e:
            if queue:
                queue.put({'type': 'finished', 'result': {'success': False, 'error': str(e)}})
            return {
                'success': False,
                'error': str(e)
            }

    def update_config(self, settings):
        """Update configuration settings"""
        try:
            config.MIN_KEY_LENGTH = int(settings.get('min_key_length', config.MIN_KEY_LENGTH))
            config.MAX_KEY_LENGTH = int(settings.get('max_key_length', config.MAX_KEY_LENGTH))
            config.EXPECTED_IOC = float(settings.get('expected_ioc', config.EXPECTED_IOC))
            config.TARGET_FITNESS = float(settings.get('target_fitness', config.TARGET_FITNESS))
            config.MAX_ITERATIONS = int(settings.get('max_iterations', config.MAX_ITERATIONS))
            config.USE_PARALLEL = bool(settings.get('use_parallel', config.USE_PARALLEL))
            config.MAX_WORKERS = int(settings.get('max_workers', config.MAX_WORKERS))
            config.MIN_SHUFFLE_GROUP = int(settings.get('min_shuffle_group', config.MIN_SHUFFLE_GROUP))
            config.MAX_SHUFFLE_GROUP = int(settings.get('max_shuffle_group', config.MAX_SHUFFLE_GROUP))
            return True
        except ValueError:
            return False

    def run_polybius_decoder(self, cipher_text, initial_key=None, progress_callback=None):
        """Handle Polybius cipher decoding"""
        if progress_callback:
            self.polybius_cracker.progress_callback = progress_callback
            
        try:
            plaintext, key, score = self.polybius_cracker.decrypt(cipher_text, initial_key)
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