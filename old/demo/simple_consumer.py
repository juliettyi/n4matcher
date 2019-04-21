from kafka import KafkaConsumer
from kafka import KafkaProducer

import argparse
import json

parser = argparse.ArgumentParser(description='consumer')
parser.add_argument('--id', type=int, default=0, help='id of consumer')

args = parser.parse_args()
consumer = KafkaConsumer('request',
                         group_id=str(args.id),
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for msg in consumer:
  resp = msg.value
  # transform the request
  r = [f + args.id for f in resp['value']]
  resp['result'] = r
  resp['worker_id'] = args.id
  producer.send('response', resp)
