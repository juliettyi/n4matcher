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
# where to store outputs
RESULT_DIR = 'result'
# print more info
DEBUG = False
if DEBUG:
  IMAGE_DIR = '/home/ubuntu/efs/sampleimage'
  CHUNK_SIZE = 5
  # Slightly bigger samples
  # IMAGE_DIR = '/home/ubuntu/efs/imagenet_sample1500/'
  # CHUNK_SIZE = 50
else:
  IMAGE_DIR = '/home/ubuntu/efs/imagenet/'
  CHUNK_SIZE = 50000

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
      return features.tolist()
  
    t = ArrayType(StringType())
    in_col = dataset[self._inputCol]
    return dataset.withColumn(self._outputCol, udf(f, t)(in_col))

# MASTER_ADDR = 'local[4]'
MASTER_ADDR = 'spark://10.0.0.7:7077'
spark = SparkSession.builder.master(MASTER_ADDR).appName('spark-feature-gen').getOrCreate()
sc = spark.sparkContext
# add local py files
sc.addPyFile('feature.py')
sc.addPyFile('image.py')

model = get_model()
model.save(MODEL_FILE)

files = sc.parallelize([os.path.abspath(os.path.join(IMAGE_DIR, f))
         for f in os.listdir(IMAGE_DIR)])
fn_df = spark.createDataFrame(files, StringType()).toDF('fn')
fn_df.show()
print('generate feature for {} images.'.format(fn_df.count()))

processor = ReadImageAndProcess(inputCol='fn', outputCol='feature', model=model)

batch_count = (fn_df.count() // CHUNK_SIZE) + 1
total = 0

for idx in range(batch_count):
  output_fn = 'feature_%.5d_of_%.5d' % (idx, batch_count)
  print(output_fn)

  # Split all file names into CHUNK_SIZEs
  s = fn_df.limit(CHUNK_SIZE)
  # Remove from original list.
  fn_df.subtract(s)

  # Generate feature for the chunk.
  features = processor.transform(s)
  features.show()

  total += features.count()

  fn_list = []
  feature_list = []
  for row in features.rdd.collect():
    fn_list.append(row['fn'])
    feature_list.append(np.asarray(row['feature']))

  feature_tensor = np.stack(feature_list, axis=0)
  print(feature_tensor.shape)
  np.save(os.path.join(RESULT_DIR, output_fn + '.tensor'), feature_tensor)
  with open(os.path.join(RESULT_DIR, output_fn + '.map'), 'w') as f:
    json.dump(fn_list, f)

print('{} features generated.'.format(total))
sc.stop()
