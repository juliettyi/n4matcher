'''Master matcher.

Monitor input S3 bucket

- Looks for (fn, fn.npy) pair
- Read fn.npy and send content as topic to workers
- Wait for workers answers
- Sort all workers answers and write final result to S3

'''

import boto3
import botocore
import csv
import json
import time

from kafka import KafkaProducer

IN_BUCKET = 'dl-result-yc'
OUT_BUCKET = 'dl-results-final'
WORKER_COUNT = 1

# Producer, using json format for serialization.
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Keep monitoring the bucket
s3 = boto3.resource('s3')
in_bucket = s3.Bucket(IN_BUCKET)
out_bucket = s3.Bucket(OUT_BUCKET)


def process_file(name):
  print('request {}'.format(name))
  producer.send('compare_request', name)

  inter_result_files = [
    '{}.inter.{}.json'.format(name[:-4], i) for i in range(WORKER_COUNT)]
  inter_results = []
  for irf in inter_result_files:
    while True:
      try:
        irf_o = s3.Object(OUT_BUCKET, irf).load() 
        inter_results.append(irf_o.get()['Body'].read())
      except botocore.exceptions.ClientError as e:
        print('still waiting for {}'.format(irf))
        time.sleep(1)
  print(inter_results)

  
def process_bucket():
  for o in in_bucket.objects.all():
    name = o.key
    if not name.endswith('.npy'):
      continue
    process_file(name)

    
while True:
  process_bucket()
