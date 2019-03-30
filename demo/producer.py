import boto3
import csv
import json
import s3fs
import time

from kafka import KafkaProducer

# Using s3fs to open huge s3 file as if it is local files.
fs = s3fs.S3FileSystem()

# Producer, using json format.
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

with fs.open('ycinsight/measurements-out.csv', 'r') as f:
  measures = csv.reader(f)
  # skip header
  next(measures, None)

  last_date = None
  # Every time we encounter different date, we send over these rows.
  rows = []

  for row in measures:
    cur_date = row[0][:10]
    if last_date is None:
      last_date = cur_date
      rows.append(row)
    else:
      if last_date == cur_date:
        # Accumulate rows from the same date
        rows.append(row)
      else:
        last_date = cur_date
        print('date: {}, {} rows'.format(last_date, len(rows)))
        producer.send('data', rows)
        rows = [row]
        time.sleep(2)
      
