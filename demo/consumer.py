import csv
import datetime
import json

from kafka import KafkaConsumer
from string import Template


def write_index(top1_r, top2_r):
  with open('/home/ubuntu/efs/index.tmpl', 'r') as in_f:
    src = Template(in_f.read())
    if not top2_r:
      top2_r = top1_r
    d = {
      'time1': top1_r[0],
      'lat1': str(top1_r[1]),
      'lon1': str(top1_r[2]),
      'v1': str(top1_r[3]),
      'time2': top2_r[0],
      'lat2': str(top2_r[1]),
      'lon2': str(top2_r[2]),
      'v2': str(top2_r[3]),    
     }
    r = src.substitute(d)
    with open('/home/ubuntu/efs/index.html', 'w') as out_f:
      out_f.write(r)

top1 = 0.0
top2 = 0.0
top1_r = []
top2_r = []

updated = False
last_updated = datetime.datetime.now()

# ['Captured Time', 'Latitude', 'Longitude', 'Value', 'Unit', 'Location Name', 'Device ID', 'MD5Sum', 'Height', 'Surface', 'Radiation', 'Uploaded Time', 'Loader ID']
consumer = KafkaConsumer('data', value_deserializer=json.loads)
for msg in consumer:
  rows = msg.value
  # only keep unit of cpm
  for row in rows:
    if row[4] == 'cpm':
      v = float(row[3])
      if v > top1:
        print('{} > {}'.format(v, top1))
        top1 = v
        top1_r = row
        updated = True
      elif v > top2 and abs(float(row[1]) - float(top1_r[1])) > 10 and abs(float(row[2]) - float(top1_r[2])) > 10:
        print('{} > {}'.format(v, top2))
        top2 = v
        top2_r = row
        updated = True
  if updated:
    last_updated = datetime.datetime.now()
    write_index(top1_r, top2_r)
    print(top1_r)
    print(top2_r)
    updated = False
  else:
    # reset values every 60s
    if datetime.datetime.now() - last_updated > datetime.timedelta(seconds=60):
      top1 = 0.0
      top2 = 0.0
   
