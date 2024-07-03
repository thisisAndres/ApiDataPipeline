# Databricks notebook source
# MAGIC %md
# MAGIC IMPORTS & CONFIGURATIONS

# COMMAND ----------

from datetime import date, timedelta
from pyspark.sql.functions import explode, col, to_date, lit
from py4j.protocol import Py4JJavaError
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

# COMMAND ----------

# MAGIC %md
# MAGIC EXTRACTING SOURCE API DATA

# COMMAND ----------

def mount_point_exists(mount_point:str):
    try:
        dbutils.fs.ls(mount_point)
        return True
    except:
        return False


# COMMAND ----------

if not mount_point_exists('/mnt/apidata'):
    try:
        dbutils.fs.mount(
            source="wasbs://apidata@apiprojectstorage.blob.core.windows.net",
            mount_point='/mnt/apidata',
            extra_configs={
                "fs.azure.account.key.apiprojectstorage.blob.core.windows.net": dbutils.secrets.get(scope="kv-apiPipeline", key="blb-acc-key")
            }
        )
        print('Mounted')
    except Exception as error:
        print(f'Error mounting: {error}')
else:
    print('Mount point already exists')


# COMMAND ----------

today = date.today().isoformat()
dfRaw = spark.read.json(f'/mnt/apidata/Raw_Data/weather_data_{today}.csv')

# COMMAND ----------

timelinesDf = dfRaw.select('timelines')

# COMMAND ----------

locationDf = dfRaw.select('location')

# COMMAND ----------

# MAGIC %md
# MAGIC TRANSFORMING JSON FORMAT TO TABLE

# COMMAND ----------

timelinesDf = timelinesDf.select(
    explode(col('timelines.daily')).alias('daily_data')
)

# COMMAND ----------

timelinesColumns = timelinesDf.select('daily_data.values.*').columns
locationColumns = locationDf.select('location.*').columns

# COMMAND ----------

locationDf = locationDf.select(
    *[col('location').getItem(locationColumn).alias(locationColumn) for locationColumn in locationColumns]
)
today = lit(today)
locationDf = locationDf.withColumn('time', today)\
                        .withColumnRenamed('time', 'time_location')

# COMMAND ----------

timelinesDf = timelinesDf.select(
    col('daily_data.time').alias('time'),
    *[col('daily_data.values').getItem(timelinesColumn).alias(timelinesColumn) for timelinesColumn in timelinesColumns]
)

# COMMAND ----------

timelinesDf = timelinesDf.withColumn('time', to_date(timelinesDf.time, 'yyyy-MM-dd'))

# COMMAND ----------

timelinesDf = timelinesDf.filter(timelinesDf.time == today)


# COMMAND ----------

mergedDf = timelinesDf.join(locationDf, timelinesDf.time == locationDf.time_location)\
    .drop('time_location')

# COMMAND ----------

# MAGIC %md
# MAGIC LOADING TO BLOB STORAGE

# COMMAND ----------

mergedDf.toPandas().to_parquet("/dbfs/mnt/apidata/Transformed_Data/transformed_data.parquet")
