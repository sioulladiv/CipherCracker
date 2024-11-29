import string
import random
import math
from collections import Counter
from cipher_utils import bigram_fitness  # Changed from relative to absolute import
import argparse
from config import *  # Changed from relative to absolute import
import time
from multiprocessing import Value, Array
import ctypes

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
        self.queue = None  # Add this line
        # Add shared memory variables
        self.shared_score = Value(ctypes.c_double, float('inf'))
        self.shared_text = Array(ctypes.c_char, 1000)  # Adjust size as needed
        self.shared_key = Array(ctypes.c_char, 27)  # Length of alphabet + 1
        self.start_time = None

    def update_progress(self, message):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message)

    def create_random_key(self):
        """Generate random initial substitution key"""
        letters = list(self.LETTERS)
        random.shuffle(letters)
        return ''.join(letters)

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

    def monte_carlo_optimization(self, ciphertext):
        """Optimize key using Monte Carlo with simulated annealing"""
        self.start_time = time.time()
        current_key = self.create_random_key()
        current_score = bigram_fitness(self.decrypt_with_key(ciphertext, current_key))
        self.best_key = current_key
        self.best_score = current_score
        temp = self.temperature

        for i in range(self.iterations):
            if i % 100 == 0:
                self.update_progress(f"Optimization iteration {i}/{self.iterations}")
            
            # Generate neighbor solution
            self.best_text = self.decrypt_with_key(ciphertext, self.best_key)
            new_key = self.swap_letters(current_key)
            new_score = bigram_fitness(self.decrypt_with_key(ciphertext, new_key))

            if not self.running:
                break
            
            # Calculate acceptance probability
            delta = new_score - current_score
            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_key = new_key
                current_score = new_score
                
                if current_score < self.best_score:
                    self.best_score = current_score
                    self.best_key = current_key
                    self.best_text = self.decrypt_with_key(ciphertext, current_key)
                    
                    # Update shared memory
                    self.shared_score.value = current_score
                    self.shared_text.value = self.best_text[:1000].encode()
                    self.shared_key.value = current_key.encode()
                    
                    if self.queue:
                        self.queue.put({
                            'type': 'progress',
                            'score': self.shared_score.value,
                            'text': self.shared_text.value.decode(),
                            'key': self.shared_key.value.decode()
                        })
                    self.update_progress(f"New best score: {self.best_score:.4f}")
                    if self.best_score < 0.41:
                        break
            
            # Cool down
            temp *= self.cooling_rate

        return self.best_key, self.best_score

    def decrypt(self, ciphertext):
        """Main decryption method"""
        self.update_progress("Preprocessing input text...")
        ciphertext = ''.join(c.upper() for c in ciphertext if c.isalpha())
        if not ciphertext:
            raise ValueError("No valid characters in input text")

        self.update_progress("Starting Monte Carlo optimization...")
        key, score = self.monte_carlo_optimization(ciphertext)
        plaintext = self.decrypt_with_key(ciphertext, key)

        return plaintext, key, score

def main():
    parser = argparse.ArgumentParser(description='Substitution Cipher Decoder')
    parser.add_argument('-t', '--temperature', type=float, help='Initial temperature for simulated annealing')
    parser.add_argument('-i', '--iterations', type=int, help='Number of iterations')
    args = parser.parse_args()

    cracker = SubstitutionCracker()
    if args.temperature:
        cracker.temperature = args.temperature
    if args.iterations:
        cracker.iterations = args.iterations

    ciphertext = "XK ANRD MSRDWNE, T SZBN FSTE WNFFND PTYAE KZG INWW DNEFNA, PZD T SRHN FSN XZEF EGDBDTETYQ YNIE. NJBNMFTYQ R DNBWK PDZX XTEE IRDYN T SRHN ONNY IRTFTYQ NRQNDWK PZD FSN BZEF, TY FSN SZBN FSRF ESN IZGWA ON ROWN FZ ESNA XZDN WTQSF ZY FSN XKEFNDK ZP FSN ETWHND OGWWNF. ISRF T ATA YZF NJBNMF ISNY FSN AZZDONWW DRYQ IRE FSRF XTEE IRDYN SNDENWP IZGWA ON GESNDNA TYFZ XK XZDYTYQ DZZX! ESN IRE EZXNISRF ATESNHNWWNA RYA MWZEN FZ EFRDHTYQ, RE TP ESN SRA IRWVNA SNDN, RYA TF FZZV EZXN FTXN PZD SND FZ DNMZHND NYZGQS FZ FNWW XN ISRF ESN IRE AZTYQ TY NYQWRYA. TF RBBNRDE FSRF ESN FZZV FZ SNRDF ZGD MZYMNDY FSRF FSTE XRFFND IZGWA ON ANWRKNA OK FSN MZYFTYGRW NJMSRYQN ZP WNFFNDE, RYA, ATEMZHNDTYQ FSRF FSN ESTBBTYQ MDRFNE INDN FZ ON FDRYEBZDFNA FZ NYQWRYA ZY FSN BRMTPTM ESN XRAN RDDRYQNXNYFE FZ FDRHNW ITFS FSN MRDQZ. ISRF RDDRYQNXNYFE FSZEN XTQSF SRHN ONNY ESN SRE ONNY FZZ MZK FZ NJBWRTY. PZD FSN XZXNYF T SRHN WZAQNA SND ITFS XK XRTA TY FSN RFFTM SNDN RF FSN FZINDE. FSN EFRPP SRHN ONNY XRDHNWWZGE, BDZHTATYQ SND ITFS EGTFROWN MWZFSNE, RYA ESRDTYQ XNRWE. T RX YZF EGDN SZI XTEE IRDYN ITWW XRYRQN TY FSN WZYQND FNDX, OGF PZD YZI ESN TE ENFFWNA RYA T FSTYV IN ESZGWA MZYMNYFDRFN ZGD RFFNYFTZY ZY FSN TYPZDXRFTZY FSRF ESN SRE ODZGQSF ITFS SND. QTHNY FSRF FSNDN TE R ENYETFTHTFK FZ FSTE XRFFND, T IZGWA BDNPND FZ FNWW KZG ROZGF TF TY BNDEZY. TY RYK MREN, KZG XRK INWW ITES FZ SNRD FSN EFZDK PDZX XTEE IRDYN SNDENWP, EZ T BDZBZEN FSRF IN XNNF SNDN RF SZDEWNK RF KZGD NRDWTNEF MZYHNYTNYMN. TY R MGDTZGE MZTYMTANYMN ZP FTXTYQ ETD MSRDWNE TE RWEZ BWRYYTYQ FZ HTETF ESZDFWK FZ ATEMGEE TYEFRWWTYQ STE FNWNQDRBSTM EKEFNX RF ZGD DNETANYMNE TY ZDAND FZ EBNNA MZXXGYTMRFTZY. BNDSRBE IN MRY RDDRYQN XRFFNDE EZ FSRF SN FZZ MRY ON ODTNPNA ZY FSN TEEGNE TY FSTE MREN. EBNRVTYQ ZP ODTNPTYQ, T FSTYV TF IZGWA ON RBBDZBDTRFN FZ VNNB WZDA BRWXNDEFZY TYPZDXNA ZP ZGD TYHNEFTQRFTZYE. ITFSZGF ERKTYQ FZZ XGMS RF FSTE EFRQN, FSNDN RDN ATBWZXRFTM TEEGNE RF BWRK, RYA SN XTQSF BDNPND FZ WNRA ZY FSNEN XRFFNDE. MZGWA T REV KZG FZ IDTFN FZ STX? KZG VYZI SZI SN SRFNE FZ ON OZFSNDNA OK IZXNY. TF XTQSF ON R QZZA TANR FZ NYMTBSND RWW ZGD MZXXGYTMRFTZYE ITFS STE ZPPTMN GETYQ ZGD MGEFZXRDK FDRYEBZETFTZY MTBSND. T AZ YZF NYFTDNWK FDGEF FSN ATEMDNFTZY ZP FSZEN TY STE BDTHRFN ZPPTMN. ITFS XK PZYANEF DNQRDAE, RAR"

    plaintext, key, score = cracker.decrypt(ciphertext)
    
    print(f"\nFinal Results:")
    print(f"Key: {key}")
    print(f"Score: {score:.4f}")
    print(f"Decrypted text: {plaintext[:100]}...")

if __name__ == "__main__":
    main()