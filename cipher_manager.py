from cipher_utils import bigram_fitness
import config
from ciphers import VigenereCracker, SubstitutionCracker, ShuffleCracker, PolybiusCracker, PlayfairCracker

def run_substitution_process_wrapper(cipher_text, queue):
    """Standalone wrapper function for running substitution process"""
    from ciphers.substitution import run_substitution_process
    try:
        result = run_substitution_process(cipher_text, queue)
        if queue:
            queue.put({'type': 'finished', 'result': result})
        return result
    except Exception as e:
        if queue:
            queue.put({'type': 'finished', 'result': {'success': False, 'error': str(e)}})
        return {'success': False, 'error': str(e)}

class CipherManager:
    def __init__(self):
        self.current_cipher = None
        self.crackers = {
            'vigenere': VigenereCracker(),
            'substitution': SubstitutionCracker(),
            'shuffle': ShuffleCracker(),
            'polybius': PolybiusCracker(),
            'playfair': PlayfairCracker()
        }

    def start_decoder(self, cipher_type, cipher_text, **kwargs):
        """
        Central method to handle starting any cipher decoder
        """
        self.current_cipher = cipher_type.lower()
        if self.current_cipher not in self.crackers:
            return {'success': False, 'error': f'Unknown cipher type: {cipher_type}'}

        cracker = self.crackers[self.current_cipher]
        
        # Reset running flag for fresh start
        if hasattr(cracker, 'running'):
            cracker.running = True
        
        # Set progress callback if provided
        if 'progress_callback' in kwargs:
            cracker.progress_callback = kwargs.pop('progress_callback')
        
        # Get queue 
        queue = kwargs.pop('queue', None)
        
        try:
            if self.current_cipher == 'substitution':
                return run_substitution_process_wrapper(cipher_text, queue)
            else:
                # Set target fitness on cracker instance instead of passing as parameter
                target_fitness = getattr(config, f"{self.current_cipher.upper()}_TARGET_FITNESS", 0.4)
                if hasattr(cracker, 'target_fitness'):
                    cracker.target_fitness = target_fitness
                
                # Build decrypt kwargs - include queue for shuffle cipher
                decrypt_kwargs = {
                    'forced_length': kwargs.get('forced_length'),
                    'initial_key': kwargs.get('initial_key')
                }
                
                # Add queue for shuffle cipher to enable progress updates
                if self.current_cipher == 'shuffle':
                    decrypt_kwargs['queue'] = queue
                
                # Remove None values
                decrypt_kwargs = {k: v for k, v in decrypt_kwargs.items() if v is not None}
                
                plaintext, key, score = cracker.decrypt(cipher_text, **decrypt_kwargs)
                
                # Send final result to queue
                if queue:
                    queue.put({
                        'type': 'progress',
                        'score': score,
                        'text': plaintext,
                        'key': str(key)
                    })
                
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
    
    def get_current_result(self):
        """Get the current best result from the active cracker"""
        if not self.current_cipher:
            return None
            
        cracker = self.crackers[self.current_cipher]
        if not hasattr(cracker, 'best_text'):
            return None

        result = {
            'success': True,
            'text': cracker.best_text,
            'key': cracker.best_key,
            'score': cracker.best_score
        }
        
        # Handle different text field names for different ciphers
        if self.current_cipher != 'substitution':
            result['plaintext'] = result.pop('text')
            
        return result
    
    def stop_decoder(self):
        """Stop the current running decoder"""
        if self.current_cipher and self.current_cipher in self.crackers:
            cracker = self.crackers[self.current_cipher]
            if hasattr(cracker, 'running'):
                cracker.running = False

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
            
            # Update target fitness for each cipher type
            config.TARGET_FITNESS = float(settings.get('target_fitness', 0.4))
            config.VIGENERE_TARGET_FITNESS = float(settings.get('vigenere_target_fitness', 0.4))
            config.SHUFFLE_TARGET_FITNESS = float(settings.get('shuffle_target_fitness', 0.4))
            config.POLYBIUS_TARGET_FITNESS = float(settings.get('polybius_target_fitness', 0.4))
            config.PLAYFAIR_TARGET_FITNESS = float(settings.get('playfair_target_fitness', 0.4))
            
            return True
        except ValueError:
            return False