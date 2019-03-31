import findspark
findspark.init()

# from keras.applications.imagenet_utils import preprocess_input
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from keras.preprocessing.image import img_to_array, load_img

from feature import FeatureGen

from pyspark.ml import Transformer
from pyspark.ml.image import ImageSchema
from pyspark.ml.param.shared import HasInputCol, HasOutputCol
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql import SparkSession

import json
import numpy as np
import os
import sys


MODEL_FILE = '/tmp/vgg16.h5'
IMAGE_DIR = '/home/ubuntu/efs/imagenet_sample1500/'
DEBUG = False
if DEBUG:
  IMAGE_DIR = '/home/ubuntu/efs/sampleimage'


def get_4k_model():
  base_model = VGG16(weights='imagenet')
  return Model(inputs=base_model.input, outputs=base_model.get_layer('fc2').output)

def get_model():
  return VGG16(weights='imagenet', include_top=False)


class ReadImageAndProcess(Transformer):
  def __init__(self, inputCol, outputCol, model):
    super(ReadImageAndProcess, self).__init__()
    self._inputCol = inputCol
    self._outputCol = outputCol
    self._model = model
    self._fg = FeatureGen(model)

  def _transform(self, dataset):
    def f(s):
      features = self._fg.gen_feature(s)
      if DEBUG:
        print(features.shape)
        print(np.count_nonzero(features))
        print(features)
      return features.tolist()
  
    t = ArrayType(StringType())
    in_col = dataset[self._inputCol]
    return dataset.withColumn(self._outputCol, udf(f, t)(in_col))
    

spark = SparkSession.builder.master('local').appName('test').getOrCreate()

model = get_model()
model.save(MODEL_FILE)

files = [os.path.abspath(os.path.join(IMAGE_DIR, f))
         for f in os.listdir(IMAGE_DIR)]
fn_df = spark.createDataFrame(files, StringType()).toDF('fn')
fn_df.show()
print(fn_df.count())
processor = ReadImageAndProcess(inputCol='fn', outputCol='feature', model=model)
features = processor.transform(fn_df)
features.show()
print(features.count())

