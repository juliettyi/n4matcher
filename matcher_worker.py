'''Matcher worker.

Consume topic "compare_request" 
Find local top N matches
Produce topic "compare_response"
'''
from feature.matcher import Matcher
from kafka import KafkaConsumer
from kafka import KafkaProducer

import argparse
import json
import numpy
import os
import time
import timeit

TOP_N = 10

parser = argparse.ArgumentParser(description='matcher worker')
parser.add_argument('--id', type=int, default=0, help='id of worker')
parser.add_argument('--base_dir', type=str,
                    default='/home/ubuntu/efs/feature_index',
                    help='base dir of feature index')
parser.add_argument('--index_names', type=str,
                    default='',
                    help='comma separated index dir names, for example.')

args = parser.parse_args()
start = timeit.default_timer()

assert args.index_names, 'index_names must be specified'
matchers = [
  Matcher(os.path.join(args.base_dir, n)) for n in args.index_names.split(',')
]
now = timeit.default_timer()
print('all matchers loaded. {} secs'.format(now - start))

def match_feature(feature):
  final_top = []
  for matcher in matchers:
    top = matcher.match(feature, top_n=TOP_N)
    for k in top:
      final_top.append((k, str(top[k])))

  final_top = sorted(final_top, key=lambda kv: -float(kv[1]))[:TOP_N]
  return final_top

def process_request(request):
  start = timeit.default_timer()
  npy_name = request['npy_name']
  print('got request for {}'.format(npy_name))
  feature = numpy.array(request['npy_content'])
  top_n = match_feature(feature)
  response = {
    'npy_name': npy_name,
    'worker_id': str(args.id),
    'top_n': top_n
  }
  producer.send('compare_response', response)
  now = timeit.default_timer()
  print('{}:{} secs'.format(npy_name, now - start))


consumer = KafkaConsumer('compare_request',
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for msg in consumer:
  process_request(msg.value)
  
