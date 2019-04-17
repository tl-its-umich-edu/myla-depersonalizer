import unittest, logging, os, sys

from autologging import logged, traced

# Add this path first so it picks up the newest changes without having to rebuild
this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, this_dir + "/..")

from ffx_helper import FFXEncrypt
from custom_provider import CustomProvider
import util_methods
import pandas as pd
import numpy as np

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

    def test_resample(self):
        # These will always be different values returnsd, just verify that the length is the same and they are within the original range
        test_vals = [21, 129, 123, 94]
        map_sample = util_methods.kde_resample(test_vals)
        self.assertEqual(len(map_sample), 4)
        self.assertTrue(min(test_vals) <= min(map_sample))
        self.assertTrue(max(test_vals) >= max(map_sample))

        test_vals = [0, 0, 0]
        map_sample = util_methods.kde_resample(test_vals)
        self.assertEqual(len(map_sample), 3)
        self.assertTrue(min(test_vals) <= min(map_sample))
        self.assertTrue(max(test_vals) >= max(map_sample))

    def test_shuffle(self):
        # Create a sample set of 10 users with access times every 5 minutes
        time_start = datetime.datetime(2018, 1, 1)
        data = []
        for id in range(0,20):
            # Create some sample files and 3 users
            data.append([id, f'user{id%3}',time_start + datetime.timedelta(minutes=5*id)])
        # Create the pandas DataFrame
        df = pd.DataFrame(data, columns=['file_id', 'user_id', 'access_time'])
        # Seed the randomizer so it's predictable for test
        np.random.seed(util_methods.hashStringToInt("testpasstestpass", 8))
        # Assert the 9th row is 45 minutes
        self.assertEqual(df.at[9, 'access_time'], pd.Timestamp('2018-01-01 00:45:00'))
        util_methods.shuffle(df, shuffle_col='access_time')
        # Assert the 3rd row is 45 minutes
        self.assertEqual(df.at[3, 'access_time'], pd.Timestamp('2018-01-01 00:45:00'))
        # Shuffle again but group
        df = pd.DataFrame(data, columns=['file_id', 'user_id', 'access_time'])
        # Verify the same grouping before and after for a value with time 45 minutes
        self.assertEqual(df.at[9, 'user_id'], 'user0')
        self.assertEqual(df.at[9, 'access_time'], pd.Timestamp('2018-01-01 00:45:00'))
        util_methods.shuffle(df, shuffle_col='access_time', group_col='user_id', group_by=True)
        self.assertEqual(df.at[15, 'access_time'], pd.Timestamp('2018-01-01 00:45:00'))
        self.assertEqual(df.at[15, 'user_id'], 'user0')
        
if __name__ == '__main__':
    unittest.main()
