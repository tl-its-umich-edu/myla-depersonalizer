# Utility methods for depersonalizer

import hashlib, logging
import scipy.stats
import pandas, sqlalchemy
import numpy as np
from typing import List

logger = logging.getLogger()


def hashStringToInt(s: str, length: int):
    return int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (10 ** length)


def pandasDeleteAndInsert(mysql_tables: str, df: pandas.DataFrame, engine: sqlalchemy.engine.Engine):
    """Delete from the named table and insert

    :param mysql_tables: Either a single value or | separated list of tables that will be inserted
    :type mysql_tables: str
    :param df: Either a single dataframe or one that has column names split by table_name__column_name
    :type df: pandas.DataFrame
    :param engine: SQLAlchemy engine
    :type engine: sqlalchemy.engine.Engine
    """
    mysql_tables = mysql_tables.split("|")
    for mysql_table in mysql_tables:
        # Try to split off the index
        table_name, index_name = (mysql_table.split("@") + [None] * 2)[:2]
        # Go though each table in the array
        query = f"delete from {table_name}"
        engine.execute(query)

        # write to MySQL
        if len(mysql_tables) > 1:
            table_prefix = table_name + "__"
            # Filter and Remove the table name from  column so it can be written back
            df_tmp = df.filter(regex=table_prefix)
            df_tmp = df_tmp.rename(columns=lambda x: str(x)[
                                   len(table_prefix):])
            if index_name:
                df_tmp = df_tmp.drop_duplicates(subset=index_name)
        else:
            df_tmp = df
        try:
            df_tmp.to_sql(con=engine, name=table_name,
                          if_exists='append', index=False)
        except Exception as e:
            logger.exception(f"Error running to_sql on table {table_name}")
            raise


def kde_resample(orig_data, bw_method="silverman", map_to_range=True):
    logger.debug(orig_data)

    # Needs more than 1 element to resample
    if len(orig_data) <= 1:
        return orig_data

    try:
        kde = scipy.stats.gaussian_kde(orig_data, bw_method=bw_method)
    except Exception as e:
        logger.exception("Course not handle this data")
        return orig_data


    # Generate data from kde
    raw_sample = kde.resample(len(orig_data)).T[:, 0]

    # Map the value into range if the user wants this (though it's a little slow)
    if map_to_range:
        map_sample = [int(((val - min(raw_sample)) * (max(orig_data) - min(orig_data))) / (max(raw_sample)
                                                                                           - min(raw_sample)) + min(orig_data)) for val in raw_sample]
        return map_sample
    return raw_sample


def shuffle(df, shuffle_col, group_col=None):
    """
    Shuffle a dataframe column inplace
    """
    if group_col:
        # Shuffle shuffle_col by groupCol
        df[shuffle_col] = df.groupby(group_col)[shuffle_col].transform(np.random.permutation)
    else:
        # Shuffle shuffle_col independently
        df[shuffle_col] = np.random.permutation(df[shuffle_col].values)
