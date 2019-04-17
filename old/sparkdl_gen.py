'''sparkdl feature gen.

To run:
PYSPARK_PYTHON=python3 spark-submit --packages databricks:tensorframes:0.6.0-s_2.11,databricks:spark-deep-learning:1.2.0-spark2.3-s_2.11,org.postgresql:postgresql:42.1.1 sparkdl_gen.py
'''

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark import SparkContext
from sparkdl.image import imageIO
from sparkdl import DeepImageFeaturizer
import numpy

sc = SparkContext()
spark = SparkSession(sc)

# to test, use '/home/ubuntu/imagematcher/feature/test_imgs/00001.png'
df = imageIO.readImagesWithCustomFn('/home/ubuntu/efs/imagenet_sample1500/', decode_f=imageIO.PIL_decode)
# df = imageIO.readImagesWithCustomFn('/home/ubuntu/imagematcher/feature/test_imgs', decode_f=imageIO.PIL_decode)
featurizer = DeepImageFeaturizer(inputCol='image', outputCol='features', modelName='VGG16')
df = featurizer.transform(df)

# df.show()

# df['image']: struct<origin:string,height:int,width:int,nChannels:int,mode:int,data:binary>
# df['features']: vector
# needs tranform before saving to DB.

# map image column to filename column
df = df.withColumn('fn', udf(lambda s: s.origin)('image'))
df = df.withColumn('r', udf(lambda v: numpy.array2string(numpy.array(v.toArray())))('features'))
# df.show()
# write these 2 columns to DB
df.select(*('fn', 'r')).write.format('jdbc').options(
    url='jdbc:postgresql://10.0.0.14/spark-sample15k',
    dbtable='vgg16',
    user='spark',
    driver='org.postgresql.Driver').mode('append').save()
