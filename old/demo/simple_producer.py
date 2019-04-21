import json
import random
import time

from kafka import KafkaConsumer
from kafka import KafkaProducer

# consumer = KafkaConsumer('response', value_deserializer=lambda v: json.loads(v.decode('utf-8')))
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

request_id = 0
while True:
  value = random.sample(range(100), 10)
  request = {
    'id': request_id,
    'value': value
  }
  request_id += 1
  print('sending {}'.format(request))
  producer.send('request', request)
  # for msg in consumer:
  #   response = msg.value
  #   print('got {}'.format(response))
  time.sleep(5)
