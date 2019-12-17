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
faker.seed(util_methods.hash_string_to_int(FFX_SECRET, FAKER_SEED_LENGTH))   
faker.add_provider(CustomProvider)

# This needs the string FFX_SECRET byte encoded
ffx = FFXEncrypt(FFX_SECRET)

logger.info(f"Found table {tables}")
for table in tables:
    logger.info(f"Processing {table}")
    t_config = []
    # There's a special syntax for joined tables!
    if "|" in table:
        # Figure out the tables to join and run a special query on them
        join_tables = db_config.get(table).get("tables")
        # Go thourhg each table building up the query string
        tmp_cols = []
        for join_table in join_tables:
            join_table_name = join_table.get("name")
            for join_col in join_table.get("cols"):
                # Get the column name
                join_col_name = join_col.get("name")
                # Create a new alias
                join_alias = f"{join_table_name}.{join_col_name}"
                tmp_cols.append(f"{join_table_name}.{join_col_name} AS `{join_alias}`")
                # Update the alias in the column
                join_col["name"] = join_alias
                t_config.append(join_col)
        db_cols = ",".join(tmp_cols)
        # Get the name of the first table
        db_table = join_tables[0].get("name")
        db_join = db_config.get(table).get("join")
        sql = f"SELECT {db_cols} FROM {db_table} {db_join}"
    else:
        t_config = (db_config.get(table))
        sql = f"SELECT * from {table}"
    logger.info(sql)
    df = pd.read_sql(sql, engine)
    total_rows=len(df.axes[0])
    total_cols=len(df.axes[1])
    logger.info(f"Total rows: {total_rows} cols: {total_cols}")
    logger.info(df.columns)

    # If this dataframe is empty just skip it
    if total_rows == 0 or total_cols == 0:
        continue
    # First go through the dataframe looking for cell specific changes
    # TODO: These might be able to be refactored in the future to just apply across the column!
    for row in range(total_rows):
        for col in t_config:
            # Split the module from the function name
            col_name = col.get("name")
            mod_name = col.get("module")
            method_name = col.get("method")
            if mod_name and method_name:
                dyn_func = getattr(locals().get(mod_name), method_name)
            else:
                logger.debug (f"No change indicated for {row} {col_name}")
                continue
            # Faker has no parameters
            if mod_name == "faker":
                logger.debug(f"Transforming {col_name} with Faker")
                if method_name == "date_time_on_date":
                    df.at[row, col_name] = dyn_func(df.at[row, col_name])
                else:
                    df.at[row, col_name] = dyn_func()
            elif mod_name == "ffx":
                try:
                    logger.debug(f"Transforming {col_name} with FFX")
                    df.at[row, col_name] = dyn_func(df.at[row, col_name], addition=ID_ADDITION)
                except ValueError:
                    logger.exception(f"Problem converting {df.at[row, col_name]}")
                    logger.info(np.isnan(df.at[row, col_name]))
            # else currently do nothing

    # Now go through the columns and look for column wide changes
    # These methods are based on using another column as an index 
    # and applying the changes in bulk rather than individually
    for col in t_config:
        mod_name = col.get("module")
        method_name = col.get("method")
        index_name = col.get("index")
        col_name = col.get("name")
        source_name = col.get("source")
        if mod_name and method_name:
            dyn_func = getattr(locals().get(mod_name), method_name)
        else:
            logger.debug (f"No change indicated for {col_name}")
            continue
        # TODO These are currently all "util_methods" but this should be refactored
        # since these are all nearly identical
        if method_name == "redist":
            # If it gets here it has to be numeric
            logger.debug(f"{index_name} {col_name}")
            dyn_func(df, col_name, index_name)
        elif method_name == "mean":
            logger.debug(f"{index_name} {col_name}")
            dyn_func(df, source_name, col_name, index_name)
        elif method_name == "shuffle":
            # Shuffle column inplace
            logger.debug(f"Shuffle {col_name}")
            dyn_func(df, shuffle_col=col_name, index_col=index_name)

    if (config("UPDATE_DATABASE", cast=bool, default=False)):
        util_methods.pandas_delete_and_insert(table, df, engine)

    logger.info(df.to_csv())
# Re-enable checks
if (DISABLE_FOREIGN_KEYS):
    engine.execute('SET FOREIGN_KEY_CHECKS = 1;')