import os
import os.path
import json
from concurrent.futures import ThreadPoolExecutor
from itertools import product
import pandas as pd
import numpy as np
import requests
import boto3
from datetime import datetime
import time

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

s3 = boto3.resource('s3',
                  region_name='us-east-1',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)



def get_interval(min_ts: int, end_ts: int, active_id:int, step:int):

    """
    This function builds an array of intervals.

    params:
        min_ts: minimum integer timestamp
        end_ts: maximum integer timestamp
        active_id: currency pair code
        step: the interval's distance
    """
    #Initiate an empty numpy array
    interval = np.empty([0, 2], dtype=int)

    #Iterates over end_ts to get all the possible intervals
    for end in range(end_ts, min_ts, -step):

        #start_ts should be the end_ts minus the step
        start_ts = end - step

        #Lock start_ts to stop at min_ts
        if start_ts < min_ts:
            start_ts = min_ts + 1000

        #Appends start_ts and end_ts to the empty array
        interval = np.append(interval, np.array([[start_ts, end]]), axis=0)

    #Get all possible combinations from interval and active_ids
    api_calls = list(product(interval, active_id))

    return api_calls


def get_data(api_call:list , date:str):

    """
    This function makes an api call and return its response in a data frame.

    params:
        api_call: url params to make an api call
        date: date of extraction
    """

    api_call = api_call

    #Api url string
    api_url = 'https://cdn.iqoption.com/api/quotes-history/quotes/3.0?to={max_date}&from={min_date}&active_id={active_id}&only_round=true&_key=1614903660000'

    #Insert interval into api url string
    api_url = api_url.format(max_date=str(api_call[0][1]), min_date=str(api_call[0][0]), active_id=str(api_call[1]))
    print(api_url)
    #Makes the api call
    page = requests.get(api_url)

    #Parses the data into a json format
    response = json.loads(page.text)

    #Converts json into a data frame format
    response = pd.DataFrame(response['quotes'])

    #Adding active_id value to df
    response['active_id'] = api_call[1]

    #Create active_id dir
    active_id_dir = os.path.join(os.path.dirname(__file__), "csvs/{}".format(str(api_call[1])))

    if not os.path.exists(active_id_dir):
        try:
            os.makedirs(active_id_dir)
        except:
            pass

    #Create date dir
    date_dir = os.path.join(os.path.dirname(__file__), "csvs/{}/{}".format(str(api_call[1]), str(date)))

    if not os.path.exists(date_dir):
        try:
            os.makedirs(date_dir)
        except:
            pass

    #Save it to a csv file
    filepath = 'csvs/{active_id}/{date}/from_{min_interval}_to_{max_interval}.csv'.format(date=str(date),
                                                                                          min_interval=str(int(api_call[0][0]/1000)),
                                                                                          max_interval=str(int(api_call[0][1]/1000)),
                                                                                          active_id=str(api_call[1]))

    s3_filepath = '{active_id}/{date}/from_{min_interval}_to_{max_interval}.csv'.format(date=str(date),
                                                                                          min_interval=str(int(api_call[0][0]/1000)),
                                                                                          max_interval=str(int(api_call[0][1]/1000)),
                                                                                          active_id=str(api_call[1]))
    file_dir = os.path.join(os.path.dirname(__file__), filepath)
    response.to_csv(file_dir, sep = ";", header=True, index=False)
    s3.meta.client.upload_file(
        file_dir,
        'udac-forex-project',
        s3_filepath
    )


def process_data(api_calls:list, date:str, n_threads:int = 1):
    """
    """
    futures = []
    print("df initialized")
    for i in api_calls:
        print(i)
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        print("ThreadPoolExecutor initialized")
        for row in api_calls:
            print("running function for: {}".format(row))
            futures.append(executor.submit(get_data, row, date))
            print("submitted")
    executor.shutdown()
    results = [f.result() for f in futures]
    #df = df.append(results, ignore_index=True)
    return results


def run_etl(min_ts:int, end_ts:int, step:int, active_id:list, date:str):
    """
    """
    print("Fetching interval list")
    api_calls = get_interval(min_ts=min_ts, end_ts=end_ts, active_id=active_id, step=step)
    print("Inverval list built")
    #Processing data
    print("Processing data")
    processed_data = process_data(api_calls, date, n_threads=8)


def insert_data(df, destfile:str, mode:str):
    """
    """
    data = df
    current_dir = os.path.dirname(__file__)
    print("Inserting rows into file")
    data.to_csv(os.path.join(current_dir, destfile), sep = ";", mode=mode, header=False, index=False)
    return print("Rows inserted: {}".format(df.shape[0]))
