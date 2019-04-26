# This script reads from a MySQL server the table structure and based on the configuration file (config.json) returns encrypted/anonymized data
import os, logging, sys, json, inspect

from faker import Faker
from custom_provider import CustomProvider

from dotenv import load_dotenv
from decouple import config, Csv

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from ffx_helper import FFXEncrypt

import util_methods

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

# Add this path first so it picks up the newest changes without having to rebuild
this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, this_dir + "/..")

load_dotenv(dotenv_path=this_dir + "/.env")

with open(this_dir + "/config.json") as json_data:
    db_config = json.load(json_data)
    logger.info (db_config)

# get the tables to run based on they keys in the config
tables = config("TABLES", cast=Csv(), default="")
# If the user doesn't specify specific tables just run them all
if not(tables):
    tables = db_config.keys()

# Get the prefix and secret to use with FFX
ID_ADDITION = config("ID_ADDITION", cast=int, default=0)
FFX_SECRET = config("FFX_SECRET", cast=str, default="")

DISABLE_FOREIGN_KEYS = config("DISABLE_FOREIGN_KEYS", cast=bool, default=False)

# Connect up to the database
engine = create_engine(f"mysql://{config('MYSQL_USER')}:{config('MYSQL_PASSWORD')}@{config('MYSQL_HOST')}:{config('MYSQL_PORT')}/{config('MYSQL_DATABASE')}?charset=utf8")

#Disable foreign key checks
if (DISABLE_FOREIGN_KEYS):
    engine.execute('SET FOREIGN_KEY_CHECKS = 0;')

FAKER_SEED_LENGTH = config("FAKER_SEED_LENGTH", cast=int, default=0)

faker = Faker()
faker.seed(util_methods.hashStringToInt(FFX_SECRET, FAKER_SEED_LENGTH))   
faker.add_provider(CustomProvider)

# This needs the string FFX_SECRET byte encoded
ffx = FFXEncrypt(FFX_SECRET)

logger.info(f"Found table {tables}")
for table in tables:
    logger.info(f"Processing {table}")
    t_config = (db_config.get(table))
    df = pd.read_sql(f"SELECT * from {table}", engine).infer_objects()
    total_rows=len(df.axes[0])
    total_cols=len(df.axes[1])
    
    # First go through the dataframe looking for cell specific changes
    # TODO: These might be able to be refactored in the future to just apply across the column!
    for row in range(total_rows):
        for col in t_config:
            # Split the module from the function name
            col_name = col.get('name')
            mod_name, func_name = (col.get('method').rsplit('.', 1) + [None] * 2)[:2]
            if "None" in mod_name:
                logger.debug (f"No change indicated for {row} {col_name}")
            # Faker has no parameters
            elif "faker" in mod_name:
                logger.debug("Transforming with Faker")
                func = getattr(locals().get(mod_name), func_name)
                if func_name == "date_time_on_date":
                    df.at[row, col_name] = func(df.at[row, col_name])
                else:
                    df.at[row, col_name] = func()
            elif "ffx" in mod_name:
                try:
                    logger.debug("Transforming with FFX")
                    df.at[row, col_name] = getattr(locals().get(mod_name), func_name)(df.at[row, col_name], addition=ID_ADDITION)
                except ValueError:
                    logger.exception(f"Problem converting {df.at[row, col_name]}")
                    logger.info(np.isnan(df.at[row, col_name]))
            elif "TODO" in "mod_name":
                logger.info(f"{row} {col_name} marked with TODO, skipping")
            # else currently do nothing

    # Now go through the columns and look for column wide changes
    # These methods are based on using another column as an index 
    # and applying the changes in bulk rather than individually
    for col in t_config:
        mod_name, index_name = (col.get('method').rsplit('.', 1) + [None] * 2)[:2]
        col_name = col.get('name')
        if "redist" in mod_name:
            # If it gets here it has to be numeric
            logger.debug(f"{index_name} {col_name}")
            df[col_name] = pd.to_numeric(df[col_name])
            df[col_name].fillna(value=0, inplace=True)
            df[col_name] = df.groupby([index_name])[col_name].transform(lambda x: util_methods.kde_resample(x))
        if "mean" in mod_name:
            logger.debug(f"{index_name} {col_name}")
            # This is a special case variable that averages a column on an index
            avg_col, index_name = (index_name.rsplit('__', 1))
            df[avg_col] = pd.to_numeric(df[avg_col])
            df[avg_col].fillna(value=0, inplace=True)
            df[avg_col].replace('None', pd.np.nan, inplace=True)
            df[col_name] = df.groupby([index_name])[avg_col].transform(lambda x: round(x.mean(), 2))
        if "shuffle" in mod_name:
            # Shuffle column inplace
            logger.debug(f"Shuffle {col_name}")
            df[col_name].fillna(value=0, inplace=True)
            util_methods.shuffle(df, shuffle_col= col_name, group_col=index_name)

    # If the database should be updated, call to update
    if (config("UPDATE_DATABASE", cast=bool, default=False)):
        util_methods.pandasDeleteAndInsert(table, df, engine)

    logger.info(df.to_csv())
# Re-enable checks
if (DISABLE_FOREIGN_KEYS):
    engine.execute('SET FOREIGN_KEY_CHECKS = 1;')