# Databricks notebook source
# MAGIC %md
# MAGIC IMPORTS

# COMMAND ----------

from datetime import date, timedelta
from pyspark.sql.functions import explode, col, to_date
from py4j.protocol import Py4JJavaError

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

# MAGIC %md
# MAGIC TRANSFORMING JSON FORMAT TO TABLE

# COMMAND ----------

expandedDf = timelinesDf.select(
    explode(col('timelines.daily')).alias('daily_data')
)

# COMMAND ----------

fields = expandedDf.select('daily_data.values.*').columns

# COMMAND ----------

df_flattened = expandedDf.select(
    col('daily_data.time').alias('time'),
    *[col('daily_data.values').getItem(field).alias(field) for field in fields]
)

# COMMAND ----------

df_flattened = df_flattened.withColumn('time', to_date(df_flattened.time, 'yyyy-MM-dd'))

# COMMAND ----------

df_flattened = df_flattened.filter(df_flattened.time == today)

# COMMAND ----------


