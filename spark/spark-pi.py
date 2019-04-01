import findspark
findspark.init()

from pyspark.sql import SparkSession

import pyspark
import random

# local with 4 cores
# MASTER_ADDR = 'local[4]'
# distributively
MASTER_ADDR = 'spark://10.0.0.7:7077'
spark = SparkSession.builder.master(MASTER_ADDR).appName('spark-feature-gen').getOrCreate()
sc = spark.sparkContext

num_samples = 10 * 1000 * 1000

def inside(p):
  x, y = random.random(), random.random()
  return x*x + y*y < 1

count = sc.parallelize(range(0, num_samples)).filter(inside).count()
pi = 4.0 * count / num_samples
print(pi)

sc.stop()
