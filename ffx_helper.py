import pyffx

import string, logging, sys
import re
import numpy as np
from autologging import logged, traced
import random

logger = logging.getLogger()

@logged
class FFXEncrypt():

    def __init__(self, ffx_secret: str):
        if len(ffx_secret) < 16:
            logger.exception("The length of the secret should be longer than 16, a random key will be used.")
            ffx_secret = ''.join(random.choices(string.ascii_lowercase, k=16))

        if isinstance(ffx_secret, str):
            ffx_secret = ffx_secret.encode()
        
        self.ffx_secret = ffx_secret

    def count_replace(self, s: str, old: str, new: str, max: int) -> (int, str):
        count = s.count(old)
        v = s.replace(old, new, max)
        return count, v

    def encrypt(self, val, addition: int = sys.maxsize):
        """ Encrypt a value with FFX library. Negative values are currently not supported as integers.
        :param val: Value to encrypt
        :type val: Either an integer, a string or a floating point number (represented as a string)
        :param addition: Value added to an integer number, which will be subtracted first, defaults to sys.maxsize
        :param addition: int, optional
        :return: Encrypted number fitting same format as input
        :rtype: Either an int or a string depending on what was passed in
        """
        n_val = 0
        # If the value is none or if its numpy and nan then just return it
        if val == None or (isinstance(val, np.float64) and np.isnan(val)):
            return val
        # Some floats are actually integers, convert these
        # They have to be represented as float64 becaues of NaN
        if (isinstance(val, np.float64) and val.is_integer()):
            val = np.int64(val)
        try:
            logger.debug(type(val))
            # Strings that are integers should just be int
            if isinstance(val, str) and val.isdigit():
                val = int(val)
            if np.issubdtype(type(val), np.int64) and val > 0: # If val is Integer
                # If there's an addition do the new calculation
                n_val = val - addition
                logger.debug(f"n_val = {n_val} val = {val} addition = {addition}")
                if n_val > 0:
                   val = n_val
                e = pyffx.Integer(self.ffx_secret, length=len(str(val)))
                enc = e.encrypt(val)
            else: # Either String or Decimal
                val = str(val)
                enc = ""
                elems = re.split('(\W+|\d+)', val)
                for elem in elems:
                    if len(elem) == 0:
                        continue
                    vlen = len(elem)
                    if elem.isdigit():
                        # encrypt integer part
                        e = pyffx.Integer(self.ffx_secret, length=vlen)
                        temp = str(e.encrypt(elem))
                    elif elem.isalpha():
                        # encrypt alphabet characters
                        if elem.islower():
                            e = pyffx.String(self.ffx_secret, alphabet=string.ascii_lowercase, length=vlen)
                        elif elem.isupper():
                            e = pyffx.String(self.ffx_secret, alphabet=string.ascii_uppercase, length=vlen)
                        else:
                            e = pyffx.String(self.ffx_secret, alphabet=string.ascii_letters, length=vlen)
                        temp = e.encrypt(elem)
                    else: # Escape special characters
                        temp = elem
                    enc += str(temp)

            logger.debug(f"Out val {enc}")  
            # Return it as a string 
            if np.issubdtype(type(val), np.int64) and n_val > 0:
                enc += addition
            return enc
        except Exception as e:
            logger.exception(f"Cannot encrypt {val} {type(val)}")
            return val