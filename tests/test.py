import unittest, logging, os, sys

from autologging import logged, traced

# Add this path first so it picks up the newest changes without having to rebuild
this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, this_dir + "/..")

from ffx_helper import FFXEncrypt
from custom_provider import CustomProvider
import util_methods

import datetime

from faker import Faker

logging.basicConfig(level=os.getenv("log_level", "TRACE"))

@logged
class TestAnonymizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ffx = FFXEncrypt("passwordpassword")
        cls.faker = Faker()
        cls.faker.add_provider(CustomProvider)

    def test_ffx_encrypt(self):
        self.assertEqual(self.ffx.encrypt("ABC"), 'HZC')
    def test_ffx_prefix(self):
        self.assertEqual(self.ffx.encrypt(123456, addition=123000), 123000+self.ffx.encrypt(456))
        # Test if no prefix found
        self.assertEqual(self.ffx.encrypt(995), 643)
    def test_ffx_font_case(self):
        self.assertEqual(self.ffx.encrypt("something"), "zkcofcwmq")
        self.assertEqual(self.ffx.encrypt("someTHing"), "KHbVXLxYV")
        self.assertEqual(self.ffx.encrypt("SOMETHING"), "ZKCOFCWMQ")
    def test_ffx_decimal(self):
        self.assertEqual(self.ffx.encrypt('10.123'), '80.680')
        self.assertEqual(self.ffx.encrypt('0.123'), '4.680')
        self.assertEqual(self.ffx.encrypt('.567'), '.80')
        self.assertEqual(self.ffx.encrypt('-100.0'), '-149.4')
        self.assertEqual(self.ffx.encrypt('23.55'), '58.68')
        self.assertEqual(self.ffx.encrypt('-.567'), '-.80')
        self.assertEqual(self.ffx.encrypt('-12.567'), '-25.80')
        self.assertEqual(self.ffx.encrypt('6.000'), '0.923')
        self.assertEqual(self.ffx.encrypt('1.23E-2'), '5.58C-6')
        self.assertEqual(self.ffx.encrypt('-1.23e2'), '-5.58c6')
    def test_ffx_special(self):
        self.assertEqual(self.ffx.encrypt('test@example.com'), 'cafw@uegmpnf.vxj')
        self.assertEqual(self.ffx.encrypt('test@@@@gmail.colll099m'), 'cafw@@@@nyzav.ddzvu628k')
        self.assertEqual(self.ffx.encrypt('123abc.456.bda123'), '680hzc.605.qfu680')
    def test_assignment_custom(self):
        self.faker.seed(util_methods.hashStringToInt("testpasstestpass", 16))
        # pylint: disable=no-member
        self.assertEqual(self.faker.assignment(),"Practice Assignment #196")
        # pylint: disable=no-member
        self.assertEqual(self.faker.assignment(), "Architecture Assignment #819")

    def test_date_time_on_date(self):
        self.faker.seed(util_methods.hashStringToInt("testpasstestpass", 16))
        # pylint: disable=no-member
        self.assertEqual(self.faker.date_time_on_date(datetime.datetime(2019, 1, 1, 1, 1, 1)), datetime.datetime(2019, 1, 1, 6, 58, 12))

        # Adding the string case for date_time_on_date
        # pylint: disable=no-member
        self.assertEqual(self.faker.date_time_on_date("2019-05-01 13:14:15"), datetime.datetime(2019, 5, 1, 11, 58, 39))
        
    def test_course_id(self):
        self.faker.seed(util_methods.hashStringToInt("testpasstestpass", 16))
        self.assertEqual(self.faker.course(),"AUTO 296 006 FA 2073")
        self.assertEqual(self.faker.course(), "AUTO 273 007 SP 2026")

if __name__ == '__main__':
    unittest.main()