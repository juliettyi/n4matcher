'''Master matcher.

Monitors dl-result-yc bucket

- Looks for (fn, fn.npy) pair
- Read fn.npy and send content as topic to workers
- Wait for workers answers
- Sort all workers answers and write final result to dl-results-final

'''

import boto3
import csv
import json

from kafka import KafkaConsumer
from kafka import KafkaProducer

BUCKET = 'dl-result-yc'

# Producer, using json format for serialization.
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))
consumer = KafkaConsumer('compare_result',
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))

# Keep monitoring the bucket
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET)

for o in bucket.objects.all():
  name = o.key
  print('request {}'.format(name))
  producer.send('compare_request', name)
  # for msg in consumer:
  #   print(msg.value)
      
