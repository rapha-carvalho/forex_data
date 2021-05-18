import pandas as pd
from datetime import datetime
from datetime import timedelta
import yfinance as yf
from pandas_datareader import data as pdr
from connect_postgres import PostgresConnect
#Dow Jones - ^DJI
#FTSE 100 - ^FTSE
#Euro Stoxx 50 - ^STOXX50E
#Nikkei 225 - ^N225


def insert_financial_index_data ():

    #Stablishing connection to redshift
    conn = PostgresConnect()
    today = datetime.now().strftime('%Y-%m-%d')

    ## Downloading index data ##

    #USA's index
    dow_jones = pdr.get_data_yahoo("^DJI", start="2021-05-01", end=today).reset_index()
    dow_jones['Country'] = 'USD'

    #Europe's index
    stoxx_50 = pdr.get_data_yahoo("^STOXX50E", start="2021-05-01", end=today).reset_index()
    stoxx_50['Country'] = 'EUR'

    #United Kingdom's index
    ftse = pdr.get_data_yahoo("^GBP", start="2021-05-01", end=today).reset_index()
    ftse['Country'] = 'GBP'

    #Japan's index
    nikkei_225 = pdr.get_data_yahoo("^N225", start="2021-05-01", end=today).reset_index()
    nikkei_225['Country'] = 'JPY'

    #Concatenate dataframes
    data = pd.concat([dow_jones, stoxx_50, nikkei_225], ignore_index=True)
    data.drop('Adj Close',axis='columns', inplace=True)

    #Insert data into redshift
    #conn.insert_data_redshift(df=data, schema="forex", table="financial_index")
    print(data.to_string())


if __name__ == '__main__':
    insert_financial_index_data()
