import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark import SparkContext

sc = SparkContext()
spark = SparkSession(sc)

from sparkdl.image import imageIO
from sparkdl import DeepImageFeaturizer

images_df = imageIO.readImagesWithCustomFn('/home/ubuntu/imagematcher/feature/test_imgs/', decode_f=imageIO.PIL_decode)
featurizer = DeepImageFeaturizer(inputCol="image", outputCol="features", modelName="InceptionV3")
df = featurizer.transform(images_df)
df.show()
