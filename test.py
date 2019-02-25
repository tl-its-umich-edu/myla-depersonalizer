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
        self.assertEqual(self.ffx.encrypt("ABC"), 'FCG')
    def test_ffx_prefix(self):
        self.assertEqual(str(self.ffx.encrypt(123456, 123)), '123'+str(self.ffx.encrypt(456)))
        # Test if no prefix found
        self.assertEqual(self.ffx.encrypt(12345, prefix=98765), 4513)
    def test_ffx_prefix_zeros(self):
        #995 encrypts to 68, it should be padded with a prefix
        self.assertEqual(self.ffx.encrypt(995), 68)
        self.assertEqual(self.ffx.encrypt(9995, 9), 9068)
    def test_ffx_font_case(self):
        self.assertEqual(self.ffx.encrypt("something"), "vdnovqovo")
        self.assertEqual(self.ffx.encrypt("someTHing"), "cLxUGFKus")
        self.assertEqual(self.ffx.encrypt("SOMETHING"), "VDNOVQOVO")
    def test_ffx_decimal(self):
        self.assertEqual(self.ffx.encrypt('10.123'), '73.453')
        self.assertEqual(self.ffx.encrypt('0.123'), '2.453')
        self.assertEqual(self.ffx.encrypt('.567'), '.909')
        self.assertEqual(self.ffx.encrypt('-100.0'), '-79.2')
        self.assertEqual(self.ffx.encrypt('23.55'), '82.34')
        self.assertEqual(self.ffx.encrypt('-.567'), '-.909')
        self.assertEqual(self.ffx.encrypt('-12.567'), '-14.909')
        self.assertEqual(self.ffx.encrypt('6.000'), '8.779')
        self.assertEqual(self.ffx.encrypt('1.23E-2'), '2.8479')
        self.assertEqual(self.ffx.encrypt('-1.23e2'), '-453.2')


if __name__ == '__main__':
    unittest.main()