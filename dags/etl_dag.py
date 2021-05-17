import __init__
from airflow import DAG
import os
from plugins.execute_query import ExecuteQueryOperator
from plugins.insert_data_redshift import StageToRedshiftOperator
from plugins.data_quality import DataQualityOperator
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from scripts.load_data_to_s3 import load_data_to_s3
from scripts.delete_csvs import delete_csvs
from scripts.remove_s3_files import remove_s3_files
from sql_queries import *

default_args = {
    'owner': 'udacity',
    'depends_on_past':False,
    'catchup':False,
    'email_on_retry':False,
    'catchup':False
}

dag = DAG('etl',
          default_args=default_args,
          start_date= datetime(2021, 5, 13),
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='@daily'
        )

create_main_table = ExecuteQueryOperator(
    task_id = 'create_main_table',
    dag=dag,
    redshift_conn_id="redshift",
    query=CREATE_MAIN_TABLE
)

create_dim_table = ExecuteQueryOperator(
    task_id = 'create_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    query=CREATE_ACTIVE_DIM_TABLE
)

load_dim_table = ExecuteQueryOperator(
    task_id = 'load_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    query=INSERT_ACTIVE_DIM_TABLE
)


loading_data_to_s3 = PythonOperator(
    dag=dag,
    task_id='loading_data_to_s3',
    python_callable=load_data_to_s3
)

removing_local_files = PythonOperator(
    dag=dag,
    task_id='removing_local_files',
    python_callable=delete_csvs
)



run_spark_job = DockerOperator(
    dag=dag,
    task_id='run_spark_job',
    auto_remove=True,
    force_pull=True,
    image='raphacarvalho/udac_spark'
)

consolidated_data_to_redshift = StageToRedshiftOperator(
    task_id='insert_data_redshift',
    dag=dag,
    table="forex.binary_options_historical_quotes",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udac-forex-project",
    s3_key="consolidated_data",
    region="us-east-1",
)

remove_s3_files = PythonOperator(
    task_id = 'remove_s3_files',
    dag=dag,
    python_callable=remove_s3_files
)


run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
   quality_tests=[
    { 'test_name':'No duplicate data', 'sql':'WITH duplicated_records AS (SELECT date_seconds, COUNT(*) FROM forex.binary_options_historical_quotes GROUP BY 1 HAVING COUNT(*) > 3) SELECT COUNT(*) FROM duplicated_records', 'expected_result': 0 },
    { 'test_name':'No seconds gap', 'sql':'WITH no_seconds_gap AS (SELECT DATE_PART(epoch, date_seconds) AS current, active_id, LEAD (DATE_PART(epoch, date_seconds), 1) OVER (PARTITION BY active_id ORDER BY DATE_PART(epoch, date_seconds)) AS next, next - current AS sec_dif FROM forex.binary_options_historical_quotes ORDER BY 1, 2) SELECT COUNT(*) FROM no_seconds_gap WHERE sec_dif > 1', 'expected_result': 0 }
    ]
)


create_main_table >> create_dim_table
create_dim_table >> load_dim_table
load_dim_table >> loading_data_to_s3
loading_data_to_s3 >> removing_local_files
removing_local_files >> run_spark_job
run_spark_job >> consolidated_data_to_redshift
consolidated_data_to_redshift >> remove_s3_files
remove_s3_files >> run_quality_checks
