'''Matcher worker.

Consume topic "compare_request"
Find local top N matches
Send topic "compare_response"

'''

import json
from kafka import KafkaConsumer
from kafka import KafkaProducer

consumer = KafkaConsumer('compare_request',
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for msg in consumer:
  v = msg.value
  print('got {}'.format(v))
  # send result back
  producer.send('compare_result', v)
