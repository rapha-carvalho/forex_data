import os
#os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages "com.amazonaws:aws-java-sdk-bundle:1.10.1015","org.apache.hadoop:hadoop-aws:3.2.0" pyspark-shell'

os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars "/usr/local/spark-3.1.1-bin-hadoop3.2/jars/hadoop-aws-3.2.0.jar","/usr/local/spark-3.1.1-bin-hadoop3.2/jars/aws-java-sdk-bundle-1.11.1015.jar","/usr/local/spark-3.1.1-bin-hadoop3.2/jars/redshift-jdbc42-2.0.0.4.jar"'
import findspark
findspark.init()
import pyspark
from datetime import datetime
import logging
from pyspark.sql import SparkSession
import boto3


AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

s3 = boto3.client('s3',
                  region_name='us-east-1',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

s3_objects = s3.list_objects(Bucket='udac-forex-project')['Contents']

runtime_object_dict = {}
for i in s3_objects:
    runtime_object_dict[i['LastModified'].strftime('%Y-%m-%d %H:%M:%S')] = i['Key']

runtime_list = [i for i in runtime_object_dict.keys()]
max_runtime = runtime_object_dict[max(runtime_list)].split('/')[1]


spark = SparkSession \
    .builder \
    .master("local[*]") \
    .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY_ID) \
    .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY) \
    .config("spark.sql.inMemoryColumnarStorage.batchSize", "100000") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.maxResultSize", "4g") \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "500M") \
    .config("spark.executor.memoryOverhead", "884M") \
    .config("spark.sql.shuffle.partition", "2") \
    .config("spark.broadcast.blockSize", "10m") \
    .config("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false") \
    .getOrCreate()


logging.getLogger("py4j").setLevel(logging.ERROR)

bucket_url = "s3a://udac-forex-project"
file = os.path.join(bucket_url, '*/{dag_run}/*.csv'.format(dag_run=max_runtime))

data = spark.read.options(delimiter=";").csv(file, header=True).dropDuplicates()
data.createOrReplaceTempView("test")
#spark.catalog.cacheTable("test")
query = """
    SELECT
         CAST(ts AS BIGINT)  AS date_seconds,
         active_id,
         CAST(value AS float) / 100.00 AS value
    FROM test
"""
df = spark.sql(query)

logging.info("Dataset converted to pandas")


#df.write.csv("s3a://udac-forex-project/consolidated_data", mode="overwrite", header=True)

df \
    .write \
    .option('header', 'true') \
    .option('fs.s3a.committer.name', 'partitioned') \
    .option('fs.s3a.committer.staging.conflict-mode', 'replace') \
    .option("fs.s3a.fast.upload.buffer", "bytebuffer") \
    .mode('overwrite') \
    .csv(path='s3a://udac-forex-project/consolidated_data', sep=',')
