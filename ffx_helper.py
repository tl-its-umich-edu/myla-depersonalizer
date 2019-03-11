import pyffx

import string, logging, sys
import re
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
            if isinstance(val, int) and n_val > 0:
                enc += addition
            return enc
        except Exception as e:
            logger.exception(f"Cannot encrypt {val} {type(val)}")
            return val