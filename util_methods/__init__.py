# Hash 

import hashlib, logging

import pandas, sqlalchemy

logger = logging.getLogger()

def hashStringToInt(s: str, length: int):
    return int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (10 ** length)

# execute database query
def pandasDeleteAndInsert(mysql_table: str, df: pandas.DataFrame, engine: sqlalchemy.engine.Engine):
    query = f"delete from {mysql_table}"
    engine.execute(query)
    
    # write to MySQL
    try:
        df.to_sql(con=engine, name=mysql_table, if_exists='append', index=False)
    except Exception as e:
        logger.exception(f"Error running to_sql on table {mysql_table}")
        raise