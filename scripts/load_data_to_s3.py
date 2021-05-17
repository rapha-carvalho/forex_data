import time
from datetime import datetime
import pandas as pd
import numpy as np
import functions as f
import logging
from connect_postgres import PostgresConnect


def load_data_to_s3():
    #Setting up connection to redshift
    conn = PostgresConnect()
    #Getting active_ids
    active_ids = np.array([1, 2, 3])
    #Getting today date
    today = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    #Setting the step to 30'
    step = 30 * 60 * 1000
    #Getting max ts from redshift
    max_ts = conn.fetch_all("""
                   SELECT
                       MAX(date_part(epoch, date_seconds)) * 1000
                   FROM forex.binary_options_historical_quotes"""
                   )

    if max_ts[0][0] is None:
        date_from  = int(time.time()) * 1000  - (3600 * 24 * 1 * 1000)
        date_to = int(time.time()) * 1000 - (1800 * 1000)
        f.run_etl(min_ts=date_from, end_ts=date_to, step=step, active_id=active_ids, date=today)
    else:
        date_from = int(max_ts[0][0])
        date_to = int(time.time()) * 1000 - (1800 * 1000)
        f.run_etl(min_ts=date_from, end_ts=date_to, step=step, active_id=active_ids, date=today)

if __name__=='__main__':
    conn = PostgresConnect()
    step = 30 * 60 * 1000
    active_ids = np.array([1, 2, 3])
    max_ts = conn.fetch_all("""
                   SELECT
                       MAX(date_part(epoch, date_seconds)) * 1000
                   FROM forex.binary_options_historical_quotes"""
                   )

    if max_ts[0][0] is not None:
        date_from = int(max_ts[0][0])
        date_to = int(time.time()) * 1000 - (1800 * 1000)
        interval = f.get_interval(min_ts=date_from, end_ts=date_to, active_id=active_ids, step=step)
        print(date_from, date_to)
        for i in interval:
            print(i)
