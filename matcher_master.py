'''Master matcher.

Monitor input S3 bucket

- Looks for (fn, fn.npy) pair
- Send fn.npy as topic to workers

'''

import boto3
import botocore
import csv
import json
import numpy
import os
import tempfile
import time

from kafka import KafkaProducer

IN_BUCKET = 'dl-result-yc'
OUT_BUCKET = 'dl-results-final'

# Producer, using json format for serialization.
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Keep monitoring the bucket
s3 = boto3.resource('s3')
in_bucket = s3.Bucket(IN_BUCKET)
out_bucket = s3.Bucket(OUT_BUCKET)


def load_npy(npy_name):
  # load npy
  tmp = tempfile.NamedTemporaryFile()
  with open(tmp.name, 'wb') as f:
    in_bucket.download_file(npy_name, tmp.name)
    tmp.flush()
  feature = numpy.load(tmp.name)
  return feature


def process_file(npy_name):
  compare_request = {
    'npy_name': npy_name,
    'npy_content': load_npy(npy_name).tolist()
  }
  print('request {}'.format(npy_name))
  producer.send('compare_request', compare_request)


def process_bucket():
  for o in in_bucket.objects.all():
    name = o.key
    if not name.endswith('.npy'):
      continue
    process_file(name)

    # copy original image and npy.
    out_bucket.copy({
      'Bucket': IN_BUCKET,
      'Key': name
      }, name)
    
    img_name = name[:-4]
    out_bucket.copy({
      'Bucket': IN_BUCKET,
      'Key': img_name
      }, img_name)
    
    # clean up
    s3.Object(IN_BUCKET, img_name).delete()
    s3.Object(IN_BUCKET, name).delete()
    print('{} done.'.format(img_name))


print('started...')
while True:
  process_bucket()
  # for performance, this line can be commented.
  # keep it here so that the print out is less busy
  time.sleep(0.05)
