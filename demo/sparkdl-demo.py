'''demo for sparkdl feature gen.

To run:
PYSPARK_PYTHON=python3 spark-submit --packages databricks:tensorframes:0.6.0-s_2.11,databricks:spark-deep-learning:1.2.0-spark2.3-s_2.11,org.postgresql:postgresql:42.1.1 sparkdl-demo.py
'''

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark import SparkContext

sc = SparkContext()
spark = SparkSession(sc)

from sparkdl.image import imageIO
from sparkdl import DeepImageFeaturizer

# images_df = imageIO.readImagesWithCustomFn('/home/ubuntu/imagematcher/feature/test_imgs/', decode_f=imageIO.PIL_decode)
# featurizer = DeepImageFeaturizer(inputCol="image", outputCol="features", modelName="InceptionV3")

df = imageIO.readImagesWithCustomFn('/home/ubuntu/imagematcher/feature/test_imgs/00001.png', decode_f=imageIO.PIL_decode)
featurizer = DeepImageFeaturizer(inputCol='image', outputCol='features', modelName='ResNet50')
df = featurizer.transform(df)

df.show()

# df['image']: Can't get JDBC type for struct<origin:string,height:int,width:int,nChannels:int,mode:int,data:binary>
# df['features']: Can't get JDBC type for vector
# needs tranform before saving to DB.

df.write.format('jdbc').options(
    url='jdbc:postgresql://10.0.0.14/spark-test',
    dbtable='resnet50',
    user='spark',
    driver='org.postgresql.Driver').mode('append').save()

    
