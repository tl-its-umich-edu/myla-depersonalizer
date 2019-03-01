import pyffx

import string, logging, sys

from autologging import logged, traced

logger = logging.getLogger()

@logged
class FFXEncrypt():

    def __init__(self, ffx_secret: str):
        if isinstance(ffx_secret, str):
            ffx_secret = ffx_secret.encode()
        self.ffx_secret = ffx_secret

    def count_replace(self, s: str, old: str, new: str, max: int) -> (int, str):
        count = s.count(old)
        v = s.replace(old, new, max)
        return count, v

    def encrypt(self, val, addition: int = sys.maxsize):
        """ Encrypt a value with FFX library
        :param val: Vaule to encrypt
        :type val: Either an integer, a string or a floating point number (represented as a string)
        :param addition: Value added to an integer number, which will be subtracted first, defaults to sys.maxsize
        :param addition: int, optional
        :return: Encrypted number fitting same format as input
        :rtype: Either an int or a string depending on what was passed in
        """
        n_val = 0
        try:
            # Strings that are integers should just be int
            if isinstance(val, str) and val.isdigit():
                val = int(val)
            if isinstance(val, int): # If val is Integer
                # If there's an addition do the new calculation
                n_val = val - addition
                logger.debug(f"n_val = {n_val}")
                if n_val > 0:
                   val = n_val
                e = pyffx.Integer(self.ffx_secret, length=len(str(val)))
                enc = e.encrypt(val)
            else: # Either String or Decimal
                val = str(val)
                vlen = len(val)
                try: # If val is decimal 
                    fl = float(val) # Test if val is a valid decimal, otherwise val is not a numeric value
                    if 'E' in val or 'e' in val: # If val is in scientific notation
                        val = str(fl)

                    neg = False
                    enc = ""
                    
                    if val.startswith('-'):
                        val = val[1:]
                        neg = True
                    
                    if '.' in val:
                        first, second = val.split('.')
                        first_encrypt = ""
                        second_encrypt = ""
                        
                        if first != "" and first.isdigit():
                            e_1 = pyffx.Integer(self.ffx_secret, length=len(first))
                            first_encrypt = e_1.encrypt(first)
                        if second != "" and second.isdigit():
                            e_2 = pyffx.Integer(self.ffx_secret, length=len(second))
                            second_encrypt = e_2.encrypt(second)
                        enc = '.'.join([str(first_encrypt), str(second_encrypt)])
                    
                    if neg:
                        enc = '-' + str(enc)

                except ValueError: # If val is String, the first float cast will throw a ValueError
                    # Test if lowercase or uppercase or mixed
                    if val.islower():
                        e = pyffx.String(self.ffx_secret, alphabet=string.ascii_lowercase, length=vlen)
                    elif val.isupper():
                        e = pyffx.String(self.ffx_secret, alphabet=string.ascii_uppercase, length=vlen)
                    else:
                        e = pyffx.String(self.ffx_secret, alphabet=string.ascii_letters, length=vlen)
                    enc = e.encrypt(val)

            logger.debug(f"Out val {enc}")  
            # Return it as a string 
            if isinstance(val, int) and n_val > 0:
                enc += addition
            return enc
        except Exception as e:
            logger.exception(f"Cannot encrypt {val} {type(val)}")
            return val