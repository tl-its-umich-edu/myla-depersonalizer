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
        cls.ffx = FFXEncrypt("testpass")
        cls.faker = Faker()
        cls.faker.add_provider(CustomProvider)

    def test_ffx_encrypt(self):
        self.assertEqual(self.ffx.encrypt("ABC"), 'FCG')
    def test_ffx_prefix(self):
        self.assertEqual(self.ffx.encrypt(123456, addition=123000), 123000+self.ffx.encrypt(456))
        # Test if no prefix found
        self.assertEqual(self.ffx.encrypt(995), 68)
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
        self.assertEqual(self.ffx.encrypt('1.23E-2'), '3.82Q-4')
        self.assertEqual(self.ffx.encrypt('-1.23e2'), '-3.82q4')
    def test_ffx_special(self):
        self.assertEqual(self.ffx.encrypt('test@example.com'), 'fjjs@qdhieex.lgs')
        self.assertEqual(self.ffx.encrypt('test@@@@gmail.colll099m'), 'fjjs@@@@aibdq.whecu236y')
        self.assertEqual(self.ffx.encrypt('123abc.456.bda123'), '453fcg.982.cle453')
    def test_assignment_custom(self):
        self.faker.seed(util_methods.hashStringToInt("testpass", 8))
        # pylint: disable=no-member
        self.assertEqual(self.faker.assignment(),"Information Assignment #531")
        # pylint: disable=no-member
        self.assertEqual(self.faker.assignment(),"Architecture Assignment #916")

    def test_date_time_on_date(self):
        self.faker.seed(util_methods.hashStringToInt("testpass", 8))
        # pylint: disable=no-member
        self.assertEqual(self.faker.date_time_on_date(datetime.datetime(2019, 1, 1, 1, 1, 1)), datetime.datetime(2019, 1, 1, 18, 53, 31))

        # Adding the string case for date_time_on_date
        # pylint: disable=no-member
        self.assertEqual(self.faker.date_time_on_date("2019-05-01 13:14:15"), datetime.datetime(2019, 5, 1, 12, 31, 18))
        
    def test_course_id(self):
        self.faker.seed(util_methods.hashStringToInt("testpass", 8))
        self.assertEqual(self.faker.course(),"AUTO #631 #006 SP 2064")
        self.assertEqual(self.faker.course(), "LATIN #270 #003 SP 2024")

if __name__ == '__main__':
    unittest.main()