import pyffx

import string, logging

from autologging import logged, traced

logger = logging.getLogger()

@logged
class FFXEncrypt():

    def __init__(self, ffx_secret: str):
        self.ffx_secret = ffx_secret

    def count_replace(self, s: str, old: str, new: str, max: int) -> (int, str):
        count = s.count(old)
        v = s.replace(old, new, max)
        return count, v

    #Encrypt with FFX!
    # TODO: Handle Decimals (probably just convert to full int and ffx each part)
    def encrypt(self, val, prefix: str=''):
        # First just convert to string
        try:
            val = str(val)
            if prefix:
                prefix = str(prefix)
                (replace_count, val) = self.count_replace(val, prefix, '', 1)
                # If there was no prefix count, just remove the prefix
                if replace_count == 0:
                    prefix = ''
            # Length of the string without the prefix
            # So ffx_encrypt(1123, 1) will return the same postfix as ffx_encrypt(123)
            vlen = len(val)
            logger.debug(f"In val {val}")
            if val.isdigit(): # If val is Integer
                e = pyffx.Integer(self.ffx_secret, length=vlen)
                val = int(val)
                enc = e.encrypt(val)
                # Return it as an int
                # If the prefix and val are both numbers put the prefix in the front
                return int(prefix + str(enc).zfill(vlen))
            else: # Either String or Decimal
                val = str(val)
                try: # If val is decimal   
                    fl = float(val)
                    neg = False
                    num = ""
                    
                    if val.startswith('-'):
                        val = val[1:]
                        neg = True
                    
                    if '.' in val:
                        first, second = val.split('.')
                        first_encrypt = ""
                        second_encrypt = ""
                        
                        if first != "":
                            e_1 = pyffx.Integer(self.ffx_secret, length=len(first))
                            first_encrypt = e_1.encrypt(first)
                        if second != "": # Do we want to preserve 0.000 ? or just 0.0
                            e_2 = pyffx.Integer(self.ffx_secret, length=len(second))
                            second_encrypt = e_2.encrypt(second)
                        enc = '.'.join([str(first_encrypt), str(second_encrypt)])
                    
                    if neg:
                        enc = '-' + str(enc)

                except: # If val is String
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
                return prefix + enc
            
        except Exception as e:
            logger.warn(f"Cannot encrypt {val} {type(val)}")
            return val