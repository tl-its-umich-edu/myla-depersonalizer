import unittest, logging, os

from autologging import logged, traced

from ffx_helper import FFXEncrypt

logging.basicConfig(level=os.getenv("log_level", "TRACE"))

@logged
class TestAnon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ffx = FFXEncrypt(b"testpass")
    def test_ffx_encrypt(self):
        self.assertEqual(self.ffx.encrypt("ABC"), 'Vcn')
    def test_ffx_prefix(self):
        self.assertEqual(str(self.ffx.encrypt(123456, 123)), '123'+str(self.ffx.encrypt(456)))
        # Test if no prefix found
        self.assertEqual(self.ffx.encrypt(12345, prefix=98765), 4513)
    def test_ffx_prefix_zeros(self):
        #995 encrypts to 68, it should be padded with a prefix
        self.assertEqual(self.ffx.encrypt(995), 68)
        self.assertEqual(self.ffx.encrypt(9995, 9), 9068)

if __name__ == '__main__':
    unittest.main()
