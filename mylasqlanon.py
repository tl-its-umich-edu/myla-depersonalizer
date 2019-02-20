# This script reads from a MySQL server the table structure and based on the configuration file (config.json) returns encrypted/anonymized data
import os, logging, sys, json

from faker import Faker

from dotenv import load_dotenv
from decouple import config, Csv

import pandas as pd
from sqlalchemy import create_engine

from ffx_helper import FFXEncrypt

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
UDW_PREFIX = config("UDW_ID_PREFIX", cast=str)
FFX_SECRET = config("FFX_SECRET", cast=str, default="").encode()

# Connect up to the database
conn = create_engine(f"mysql://{config('MYSQL_USER')}:{config('MYSQL_PASSWORD')}@{config('MYSQL_HOST')}:{config('MYSQL_PORT')}/{config('MYSQL_DATABASE')}?charset=utf8")

# Setup the faker variable
faker = Faker()
ffx = FFXEncrypt(FFX_SECRET)

for table in tables:
    t_config = (db_config.get(table))
    df = pd.read_sql(f"SELECT * from {table}", conn)
    total_rows=len(df.axes[0])
    total_cols=len(df.axes[1])
    
    for row in range(total_rows):
        for col in t_config.keys():
            # Split the module from the funciton name
            mod_name, func_name = t_config.get(col).rsplit('.', 1)
            # Faker has no parameters
            if "faker" in mod_name:
                logger.debug("Transforming with Faker")
                df.at[row, col] = getattr(locals().get(mod_name), func_name)()
            elif "ffx" in mod_name:
                logger.debug("Transforming with FFX")
                df.at[row, col] = getattr(locals().get(mod_name), func_name)(df.at[row,col], prefix=UDW_PREFIX)

logger.info(df)