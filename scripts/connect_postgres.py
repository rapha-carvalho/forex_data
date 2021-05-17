import pandas as pd
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from io import StringIO

class PostgresConnect():
    """
    This class contains methods to execute queries on a PostgreSQL database.
    """
    def __init__(self):
        self.conn_info = {
        "HOST":"",
        "PORT":"",
        "DATABASE":"",
        "USER":"",
        "PASSWORD":""

        }
        self.conn_str = "host={HOST} dbname={DATABASE} port={PORT} user={USER} password={PASSWORD}".format(HOST=self.conn_info["HOST"],
                                                                                               DATABASE=self.conn_info["DATABASE"],
                                                                                               PORT=self.conn_info["PORT"],
                                                                                               USER=self.conn_info["USER"],
                                                                                               PASSWORD=self.conn_info["PASSWORD"]
                                                                                               )
        self.alch_conn_str = 'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'.format(HOST=self.conn_info["HOST"],
                                                                                            DATABASE=self.conn_info["DATABASE"],
                                                                                            PORT=self.conn_info["PORT"],
                                                                                            USER=self.conn_info["USER"],
                                                                                            PASSWORD=self.conn_info["PASSWORD"]
        )
        self.alch_conn = create_engine(self.alch_conn_str)
        self.conn = psycopg2.connect(self.conn_str)
        self.cursor = self.conn.cursor()
        self.commit = self.conn.set_session(autocommit=True)

    def exec_query(self, *sql_query):
        """
        This function executes a query without returning data.
        """
        cursor = self.cursor
        cursor.execute(*sql_query)
        self.commit
        return print("Query executed")

    def fetch_all(self, *sql_query):
        """
        This functions fetches all data.
        """
        cursor = self.cursor
        cursor.execute(*sql_query)
        return cursor.fetchall()

    def insert_data_postgres(self, df, schema, table):
        """
        This function inserts data into a specific table stored on a Postgres db.
        """
        data = df
        sio = StringIO()
        sio.write(data.to_csv(index=None, header=None))  # Write the Pandas DataFrame as a csv to the buffer
        sio.seek(0)  # Be sure to reset the position to the start of the stream

        # Copy the string buffer to the database, as if it were an actual file
        cursor = self.cursor
        cursor.copy_from(sio, "{schema}.{table}".format(schema=schema, table=table), columns=data.columns, sep=',')
        self.commit
        return print("Data inserted")

    def insert_data_redshift(self, df, schema, table):
        """
        This function inserts data into a specific table stored on Redshift.
        """
        data = df
        data.to_sql(name=table, schema=schema, con=self.alch_conn, index=False, if_exists='append')
        return print("Data inserted")

    def close(self):
        """
        This function closes the connection to the database
        """
        self.conn.close()

if __name__=="__main__":
    t = PostgresConnect()
    query = "CREATE SCHEMA IF NOT EXISTS forex"
    t.exec_query(query)
    d = {'date_seconds': ['2021-05-01 00:00:00', '2021-05-01 00:00:02'], 'active_id': [3, 1], 'value': [1.3939, 1.29303]}
    df = pd.DataFrame(data=d)
    t.insert_data_redshift(df, "forex", "binary_options_historical_quotes")
    t.close()
