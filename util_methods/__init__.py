# Hash 

import hashlib, logging
import scipy.stats
import pandas, sqlalchemy
import numpy as np

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

def kde_resample(orig_data, bw_method="silverman", map_to_range=True):
  logger.debug(orig_data)
  
  # If the original list is empty
  if not(any(orig_data)):
    return orig_data

  kde = scipy.stats.gaussian_kde(orig_data, bw_method=bw_method)

  # Generate data from kde
  raw_sample = kde.resample(len(orig_data)).T[:,0]
  
  # Map the value into range if the user wants this (though it's a little slow)
  if map_to_range:
      map_sample = [int(((val - min(raw_sample)) * (max(orig_data) - min(orig_data))) / (max(raw_sample)
        - min(raw_sample)) + min(orig_data)) for val in raw_sample]
      return map_sample
  return raw_sample

def shuffle(df, groupCol = "", shuffleCol = "", group_by = False):
  """
  Shuffle a dataframe column inplace
  """
  if group_by:
    # Shuffle shuffleCol by groupCol
    df[shuffleCol] = df.groupby(groupCol)[shuffleCol].transform(np.random.permutation)
  else:
    # Shuffle shuffleCol independently
    df[shuffleCol] = np.random.permutation(df[shuffleCol].values)