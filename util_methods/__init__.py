# Utility methods for depersonalizer

import hashlib, logging
import scipy.stats
import pandas as pd
import sqlalchemy
import numpy as np
from typing import List

logger = logging.getLogger()


def hash_string_to_int(s: str, length: int):
    return int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (10 ** length)


def pandas_delete_and_insert(mysql_tables: str, df: pd.DataFrame, engine: sqlalchemy.engine.Engine):
    """Delete from the named table and insert

    :param mysql_tables: Either a single value or | separated list of tables that will be inserted
    :type mysql_tables: str
    :param df: Either a single dataframe or one that has column names split by table_name.column_name
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
            table_prefix = table_name + "."
            # Filter and Remove the table name from  column so it can be written back
            df_tmp = df.filter(like=table_prefix)
            df_tmp.rename(columns=lambda x: str(x)[
                                   len(table_prefix):], inplace=True)
            if index_name:
                # Drop anything na then drop the duplicates if any
                df_tmp.dropna(subset=index_name.split(), inplace=True)
                df_tmp.drop_duplicates(subset=index_name, inplace=True)
        else:
            df_tmp = df
        try:
            df_tmp.to_sql(con=engine, name=table_name,
                          if_exists='append', index=False)
        except Exception:
            logger.exception(f"Error running to_sql on table {table_name}")
            raise


def kde_resample(orig_data, bw_method="silverman", map_to_range=True):
    logger.debug(orig_data)
    try:
        kde = scipy.stats.gaussian_kde(orig_data, bw_method=bw_method)
    except Exception:
        logger.info("gaussian_kde could not handle this data, original data returned.", exc_info=True)
        return orig_data


    # Generate data from kde
    raw_sample = kde.resample(len(orig_data)).T[:, 0]

    # Map the value into range if the user wants this (though it's a little slow)
    if map_to_range:
        map_sample = [int(((val - min(raw_sample)) * (max(orig_data) - min(orig_data))) / (max(raw_sample)
                                                                                           - min(raw_sample)) + min(orig_data)) for val in raw_sample]
        return map_sample
    return raw_sample


def shuffle(df:pd.DataFrame, shuffle_col:str, index_col:str=None):
    """
    Shuffle a dataframe column inplace
    """
    df[shuffle_col].fillna(value=0, inplace=True)
    if index_col:
        # Shuffle shuffle_col by groupCol
        df[shuffle_col] = df.groupby(index_col)[shuffle_col].transform(np.random.permutation)
    else:
        # Shuffle shuffle_col independently
        df[shuffle_col] = np.random.permutation(df[shuffle_col].values)

def mean(df:pd.DataFrame, avg_col:str, result_col:str, index_col:str):
    """ Calculates the mean of one column grouped by another index column 
        and stores the results inplace in col_name
    
    :param df: Data Frame
    :param avg_col: Column that's going to be used as the average
    :param index_col: Column that will be used as the index
    :param result_col: Column that will hold the result
    """
    df[avg_col] = pd.to_numeric(df[avg_col])
    df[avg_col].fillna(value=0, inplace=True)
    df[avg_col].replace('None', pd.np.nan, inplace=True)
    # Interesting bug here with this
    # https://github.com/pandas-dev/pandas/issues/17093
    df[result_col] = df.groupby([index_col])[avg_col].transform('mean')

def redist(df:pd.DataFrame, redist_col:str, index_col:str):
    """Redistributes scores within an indexed column inplace
    
    :param df: Dataframe holding the scores
    :param redist_col: Column that will be used for the redistribution
    :param index_col: Index to do the redistribution on
    """
    df[redist_col] = pd.to_numeric(df[redist_col], errors='ignore')
    df[redist_col].fillna(value=0, inplace=True)
    df[redist_col] = df.groupby([index_col])[redist_col].transform(lambda x: kde_resample(x))