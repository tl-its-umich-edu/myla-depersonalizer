# Hash 

import hashlib

def hashStringToInt(s, length):
    return int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (10 ** length)
