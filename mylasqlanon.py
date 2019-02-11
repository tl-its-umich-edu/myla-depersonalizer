import MySQLdb
import MySQLdb.cursors 

import os, logging, sys, json

from dotenv import load_dotenv
from decouple import config, Csv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

# Add this path first so it picks up the newest changes without having to rebuild
this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, this_dir + "/..")

load_dotenv(dotenv_path=this_dir + "/.env")

with open(this_dir + "/config.json") as json_data:
    db_config = json.load(json_data)
    print (db_config)

UDW_PREFIX = config("UDW_ID_PREFIX", cast=str)
FFX_SECRET = config("FFX_SECRET", cast=str, default="").encode()

db= MySQLdb.connect(host=config("MYSQL_HOST"), user=config("MYSQL_USER"), passwd=config("MYSQL_PASSWORD"), db=config("MYSQL_DATABASE"), port=config("MYSQL_PORT", cast=int), cursorclass=MySQLdb.cursors.DictCursor)

cursor= db.cursor()

cursor.execute("select table_name from information_schema.tables where table_schema=database() and (table_name not like '%auth%')")

tables = [item['table_name'] for item in cursor.fetchall()]


for table in tables:
    cursor.execute(f"desc {table}")
    tabledesc = cursor.fetchall()
    logger.info(f"Table --{table}--\n")
    # Go through all of the tables
    for tabled in tabledesc:
        # Field, Type, Null, Key, Default, Extra
        if "int" in tabled.get('Type') or "id" in tabled.get('Field'):
            logger.info(f"{tabled.get('Field')} {tabled.get('Type')}\n")
            cursor.execute(f"select {tabled.get('Field')} from {table} limit 5")
            tvalues = cursor.fetchall()
            print (tvalues)
            




