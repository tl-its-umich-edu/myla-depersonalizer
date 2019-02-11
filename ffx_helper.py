import pyffx

import string, logging

from autologging import logged, traced

logger = logging.getLogger()

@logged
class FFXEncrypt():

    def __init__(self, ffx_secret):
        self.ffx_secret = ffx_secret

    #Encrypt with FFX!
    # TODO: Handle Decimals (probably just convert to full int and ffx each part)
    # TODO: Detect if it's all upper/lower or mixed case to determine correct alphabet
    def encrypt(self, val, prefix=''):
        # First just convert to string
        try:
            val = str(val)
            if prefix:
                prefix = str(prefix)
                val = val.replace(prefix, '', 1)
            # Length of the string without the prefix
            # So ffx_encrypt(1123, 1) will return the same postfix as ffx_encrypt(123)
            vlen = len(val)
            logger.debug(f"In val {val}")
            if val.isdigit():
                e = pyffx.Integer(self.ffx_secret, length=vlen)
                val = int(val)
            else:
                e = pyffx.String(self.ffx_secret, alphabet=string.ascii_letters, length=vlen)
            enc = e.encrypt(val)
            logger.debug(f"Out val {enc}")
            # If the prefix and val are both numbers put the prefix in the front
            if type(val) is int:
                # Return it as an int
                return int(prefix + str(enc).zfill(vlen))
            # Return it as a string
            return prefix + enc
        except Exception as e:
            logger.warn(f"Cannot encrypt {type(val)}")
            return val