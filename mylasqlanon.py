# This script reads from a MySQL server the table structure and based on the configuration file (config.json) returns encrypted/anonymized data
import os, logging, sys, json, hashlib

from faker import Faker
from faker.providers import BaseProvider

from dotenv import load_dotenv
from decouple import config, Csv

import pandas as pd
from sqlalchemy import create_engine

from ffx_helper import FFXEncrypt
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

# Add this path first so it picks up the newest changes without having to rebuild
this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, this_dir + "/..")

load_dotenv(dotenv_path=this_dir + "/.env")

with open(this_dir + "/config.json") as json_data:
    db_config = json.load(json_data)
    logger.info (db_config)

# Get the tables to run based on they keys in the config
tables = db_config.keys()

# Get the prefix and secret to use with FFX
ID_ADDITION = config("ID_ADDITION", cast=int, default=0)
FFX_SECRET = config("FFX_SECRET", cast=str, default="")

# Connect up to the database
conn = create_engine(f"mysql://{config('MYSQL_USER')}:{config('MYSQL_PASSWORD')}@{config('MYSQL_HOST')}:{config('MYSQL_PORT')}/{config('MYSQL_DATABASE')}?charset=utf8")

FAKER_SEED_LENGTH = config("FAKER_SEED_LENGTH", cast=int, default=0)

# Hash 
def hashStringToInt(s, length):
    return int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (10 ** length)

# Setup the faker variable
# Faker provider for assignment
class AssignmentProvider(BaseProvider):
    def assignment(self):
        # Fake class list
        classes = [
            'Reading',
            'Video',
            'Practice',
            'Random',
            'English',
            'Archtecture',
            'Information'
        ]
        num = self.random_number(digits=3)
        clas = self.random_element(elements=(*classes,))
        return '{0} Assignment #{1}'.format(clas, num)

def date_time_on_date(date, faker):
    """
    Input: datetime
    Output: datetime with a different time on the same date
    """
    day = date.date()
    start = datetime(day.year, day.month, day.day)
    end = datetime(day.year, day.month, day.day, 23,59,59)
    return faker.date_time_between_dates(datetime_start=start, datetime_end=end)

faker = Faker()
faker.seed(hashStringToInt(FFX_SECRET, FAKER_SEED_LENGTH))   
faker.add_provider(AssignmentProvider)

# This needs the string FFX_SECRET byte encoded
ffx = FFXEncrypt(FFX_SECRET)

logger.info(f"Found table {tables}")
for table in tables:
    logger.info(f"Processing {table}")
    t_config = (db_config.get(table))
    df = pd.read_sql(f"SELECT * from {table}", conn)
    total_rows=len(df.axes[0])
    total_cols=len(df.axes[1])
    
    for row in range(total_rows):
        for col in t_config.keys():
            # Split the module from the function name
            mod_name, func_name = (t_config.get(col).rsplit('.', 1) + [None] * 2)[:2]
            if "None" in mod_name:
                logger.debug (f"No change indicated for {row} {col}")
            # Faker has no parameters
            elif "faker" in mod_name:
                logger.debug("Transforming with Faker")
                df.at[row, col] = getattr(locals().get(mod_name), func_name)()
            elif "ffx" in mod_name:
                logger.debug("Transforming with FFX")
                df.at[row, col] = getattr(locals().get(mod_name), func_name)(df.at[row,col], addition=ID_ADDITION)
            elif "TODO" in "mod_name":
                logger.info(f"{row} {col} marked with TODO, skipping")

    logger.info(df.to_csv())