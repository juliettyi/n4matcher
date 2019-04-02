import findspark
findspark.init()

# import pyspark class Row from module sql
from pyspark.sql import *
import pyspark

record = Row(fn='123456', feature='Computer Science')

spark = pyspark.SparkContext(appName="SQL")
url = "jdbc:postgresql://10.0.0.14/imagenet"
properties = {
    "driver": "org.postgresql.Driver",
}

sc = SQLContext(spark)
df = sc.read.jdbc(url=url, table='mapping', properties=properties)
