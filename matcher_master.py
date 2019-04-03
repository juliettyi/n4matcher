'''Master matcher.

Monitor input S3 bucket

- Looks for (fn, fn.npy) pair
- Send fn.npy as topic to workers
- Wait for workers answers
- Sort all workers answers and write final result to EFS/S3/...

'''

import boto3
import botocore
import csv
import json
import os
import tempfile
import time

from kafka import KafkaProducer

WORKER_COUNT = 3
TOP_N = 10

IN_BUCKET = 'dl-result-yc'
OUT_BUCKET = 'dl-results-final'

SRC_BUCKET = 'yc-insight-imagenet'
RESULT_DIR = '/home/ubuntu/efs/matcher/'
WWW = 'http://ec2-35-167-117-254.us-west-2.compute.amazonaws.com'

# Producer, using json format for serialization.
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Keep monitoring the bucket
s3 = boto3.resource('s3')
in_bucket = s3.Bucket(IN_BUCKET)
out_bucket = s3.Bucket(OUT_BUCKET)

def append_to_index(r, img_name):
  new_row = result_to_row(r, img_name)
  # save html
  index = os.path.join(RESULT_DIR, 'index.html')
  with open(index, 'a') as f:
    f.write(new_row)


def result_to_row(r, img_name):
  line = ['<table><tr>']
  # self.
  link = '{}/efs/matcher/{}.html'.format(WWW, img_name)
  line.append('<td><a href={}><img class=row_img height=224 width=224 src="https://s3-us-west-2.amazonaws.com'
                '/{}/{}" /></a></td>'.format(link, OUT_BUCKET, img_name))
  # top similar images
  for name,score in r:
    line.append('<td><img class=row_img height=224 width=224 src="https://s3-us-west-2.amazonaws.com'
                '/{}/{}" /></td>'.format(SRC_BUCKET, name))
  line.append('</tr></table>')
  return '\n'.join(line)
  

def result_to_html(r, img_name):
  line = ['<table>']
  line.append('<tr>')
  # self.
  line.append('<td><img class=src_img src="https://s3-us-west-2.amazonaws.com'
                '/{}/{}" /></td>'.format(OUT_BUCKET, img_name))
  line.append('<td>SELF</td>')
  line.append('</tr>')
  # top similar images
  for name,score in r:
    line.append('<tr>')
    line.append('<td><img class=dest_img src="https://s3-us-west-2.amazonaws.com'
                '/{}/{}" /></td>'.format(SRC_BUCKET, name))
    line.append('<td>{}</td>'.format(score))
    line.append('</tr>')
  line.append('</table>')
  return '\n'.join(line)

  
def process_file(name):
  print('request {}'.format(name))
  producer.send('compare_request', name)

  img_name = name[:-4]
  inter_result_files = [
    '{}.inter.{}.json'.format(img_name, i) for i in range(WORKER_COUNT)]
  inter_results = []
  for irf in inter_result_files:
    irf_loaded = False
    while not irf_loaded:
      try:
        print('load {}'.format(irf))
        irf_o = s3.Object(OUT_BUCKET, irf).get()
        print('loaded {}'.format(irf))
        inter_results += json.loads(irf_o['Body'].read().decode('utf-8'))
        irf_loaded = True
      except botocore.exceptions.ClientError as e:
        print('still waiting for {}'.format(irf))
        time.sleep(1)
  print('got all results. sort and take top n')
  print(inter_results)
  final_top = sorted(inter_results, key=lambda kv: -float(kv[1]))[:TOP_N]
  print(final_top)

  # clean up intermediate json files
  for irf in inter_result_files:
    s3.Object(OUT_BUCKET, irf).delete()
  
  out_fn = os.path.join(RESULT_DIR, '{}.html'.format(img_name))
  with open(out_fn, 'w') as f:
    f.write(result_to_html(final_top, img_name))
  append_to_index(final_top, img_name)

  
def process_bucket():
  for o in in_bucket.objects.all():
    name = o.key
    if not name.endswith('.npy'):
      continue
    process_file(name)

    # copy original image.
    img_name = name[:-4]
    out_bucket.copy({
      'Bucket': IN_BUCKET,
      'Key': img_name
      }, img_name)
    # clean up
    s3.Object(IN_BUCKET, img_name).delete()
    s3.Object(IN_BUCKET, name).delete()
    print('{} done.'.format(img_name))


print('started...')
while True:
  process_bucket()
  # for performance, this line can be commented.
  # keep it here so that the print out is less busy
  time.sleep(1)
