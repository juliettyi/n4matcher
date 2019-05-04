import findspark
findspark.init()

from feature import FeatureGen

from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.models import Model

from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext

import json
import numpy as np
import os
import pickle
import sys

DEBUG = False
if DEBUG:
  # IMAGE_DIR = '/home/ubuntu/efs/sampleimage'
  # Slightly bigger samples   1500
  # IMAGE_DIR = '/home/ubuntu/efs/imagenet_sample1500/'
  # Bigger samples 15000
  IMAGE_DIR = '/home/ubuntu/efs/imagenet_sample/'
else:
  # Read file list from input file
  # IMAGE_DIR = '/home/ubuntu/efs/imagenet/'
  IMAGE_DIR = None
  # First 300K was not shuffled, the remaining are shuffled.
  # FILE_LIST = '/home/ubuntu/imagematcher/index/imagenet_training_fns.txt'
  FILE_LIST = '/home/ubuntu/imagematcher/index/imagenet_training_fns_exclude_first_300K.txt'

def read_from_file_list(fn):
  with open(fn, 'r') as f:
    all = f.read()
    return all.split('\n')  

def featurize(fg, fn):
  '''Transform filename column into feature column.

  Since input data is dirty, which may contain empty / broken images
  We want to return "ERROR" for those kind of input files and skip them
  in later stage.
  '''
  try:
    f = fg.gen_feature(fn)
    return f
  except Exception as e:
    # print(e)
    # return an array with shape(0,)
    return np.array([])
 
def convert_to_str(a):
  if a.shape[0] == 0:
    return "ERROR"
  else:
    return json.dumps(a.tolist())

def load_from_str(s):
  al = json.loads(s)
  return np.array(al)
 
def main():
  # list all files under IMAGE_DIR
  if IMAGE_DIR:
    TABLE_NAME = 'vgg16all'
    files = [os.path.abspath(os.path.join(IMAGE_DIR, f))
             for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]
    appname = 'spark_gen_all'
  else:
    ROUND = 5
    # v1: first 150K of unshuffled fns
    # v2: second 150K of unshuffuled fns
    # v3: 450K shuffled (300K - 750K)
    # v4: 450K shuffled (750K - 1200K)
    # v5: remaining (1200K - 1281174)
    # so on...
    TABLE_NAME = 'vgg16v' + str(ROUND)
    # First 300K was not shuffled, the remaining are shuffled.
    FILE_LIST_START = (ROUND - 3) * 450000
    FILE_LIST_END = (ROUND - 2) * 450000
    files = read_from_file_list(FILE_LIST)
    print('{} file names loaded'.format(len(files)))
    assert len(files) > FILE_LIST_START
    files = files[FILE_LIST_START:FILE_LIST_END]
    appname = 'spark_gen_round_' + str(ROUND)

  sc = SparkContext(appName=appname)
  spark = SparkSession(sc)
  spark.catalog.clearCache()
  # add local py files
  sc.addPyFile('feature.py')

  model = VGG16(weights='imagenet', include_top=False)
  fg = FeatureGen(model)

  # a wrapped udf
  def featurize_udf(fn):
    return featurize(fg, fn)

  df = spark.createDataFrame(files, StringType()).toDF('fn')
  df = df.withColumn('feature_vector', udf(featurize_udf)('fn'))
  df = df.withColumn('feature_str', udf(convert_to_str)('feature_vector'))

  # write fn,features columns to DB
  df.select(*('fn', 'feature_str')).write.format('jdbc').options(
      url='jdbc:postgresql://10.0.0.14/spark-imagenet',
      # url='jdbc:postgresql://10.0.0.14/spark-test1',
      dbtable=TABLE_NAME,
      user='spark',
      driver='org.postgresql.Driver').mode('append').save()

if __name__ == '__main__':
  main()
