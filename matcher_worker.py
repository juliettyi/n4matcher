'''Matcher worker.

Consume topic "compare_request" 
  or watch S3 (when kafka option is turned off)
Find local top N matches
Store the results to S3

'''
from feature.matcher import Matcher
from kafka import KafkaConsumer
from kafka import KafkaProducer

import argparse
import boto3
import botocore
import json
import numpy
import os
import tempfile
import time
import timeit

IN_BUCKET = 'dl-result-yc'
OUT_BUCKET = 'dl-results-final'
TOP_N = 10

parser = argparse.ArgumentParser(description='matcher worker')
parser.add_argument('--id', type=int, default=0, help='id of worker')
parser.add_argument('--debug', type=int, default=0, help='set to 1 to debug')
parser.add_argument('--use_kafka', type=int, default=1, help='set to 0 to skip kafka')
parser.add_argument('--base_dir', type=str,
                    default='/home/ubuntu/efs/feature_index',
                    help='base dir of feature index')
parser.add_argument('--index_names', type=str,
                    default='',
                    help='comma separated index dir names, for example.')

args = parser.parse_args()
DEBUG = args.debug==1
if not DEBUG:
  assert args.index_names, 'please use start_matcher_worker.sh, or specify index_names'

s3 = boto3.resource('s3')
in_bucket = s3.Bucket(IN_BUCKET)
out_bucket = s3.Bucket(OUT_BUCKET)

start = timeit.default_timer()

if DEBUG:
  matchers = [
    Matcher('/home/ubuntu/efs/feature_index/1K'),
  ]
else:
  # 0K_10K,10K_30K,30K_50K
  # 50K_60K,60K_80K,80K_100K
  # 100K_110K,110K_130K,130K_150K
  matchers = [
    Matcher(os.path.join(args.base_dir, n)) for n in args.index_names.split(',')
  ]
  now = timeit.default_timer()
  print('all matchers loaded. {} secs'.format(now - start))

def match_file(npy_name):
  img_name = npy_name[:-4]
  print('got request for {}'.format(img_name))

  # load npy
  tmp = tempfile.NamedTemporaryFile()
  with open(tmp.name, 'wb') as f:
    in_bucket.download_file(npy_name, tmp.name)
    tmp.flush()

  feature = numpy.load(tmp.name)
  final_top = []
  for matcher in matchers:
    top = matcher.match(feature, top_n=TOP_N)
    for k in top:
      final_top.append((k, str(top[k])))

  final_top = sorted(final_top, key=lambda kv: -float(kv[1]))[:TOP_N]
  print(final_top)
  out_fn = '{}.inter.{}.json'.format(img_name, args.id)
  # save json
  tmp_json = tempfile.NamedTemporaryFile()
  with open(tmp_json.name, 'w') as f:
    json.dump(final_top, f)
  out_bucket.upload_file(tmp_json.name, out_fn)
  print('Uploaded to {}/{}'.format(OUT_BUCKET, out_fn))
  
  # send result back
  # producer.send('compare_result', v)

def process_npy_name(npy_name):
  start = timeit.default_timer()
  match_file(npy_name)
  now = timeit.default_timer()
  print('{} secs'.format(now - start))
  
def process_bucket():
  for o in in_bucket.objects.all():
    name = o.key
    if not name.endswith('.npy'):
      continue
    process_npy_name(name)

if DEBUG:
  match_file('cat.jpg.npy')
elif args.use_kafka:
  consumer = KafkaConsumer('compare_request',
                           value_deserializer=lambda v: json.loads(v.decode('utf-8')))
  # producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

  for msg in consumer:
    npy_name = msg.value
    process_npy_name(npy_name)
else:
  while True:
    process_bucket()
    # for performance, this line can be commented.
    # keep it here so that the print out is less busy
    time.sleep(1)
  
