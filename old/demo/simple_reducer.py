import json
from kafka import KafkaConsumer

consumer = KafkaConsumer('response', value_deserializer=lambda v: json.loads(v.decode('utf-8')))

for msg in consumer:
  print(msg)
  v = msg.value
  print('got ressponse {}'.format(v))
