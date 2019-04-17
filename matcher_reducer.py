'''Combine worker result.

Consume topic "compare_response"
- Wait for all workers' answers
- Sort all workers' answers and write final result to EFS/S3/...

'''

import boto3
import botocore
import json
import os
import timeit

from kafka import KafkaConsumer

WORKER_COUNT = 3
TOP_N = 10

OUT_BUCKET = 'dl-results-final'
WWW_BUCKET = 'n4result'

SRC_BUCKET = 'yc-insight-imagenet'
RESULT_DIR = '/home/ubuntu/efs/matcher/'
WWW = 'http://ec2-35-167-117-254.us-west-2.compute.amazonaws.com'

s3 = boto3.resource('s3')
www_bucket = s3.Bucket(WWW_BUCKET)

def prepend_to_index(r, img_name):
  ''' r: match result, list of file name and score tuple
      img_name: source query image
  '''    
  new_row = result_to_row(r, img_name)
  # save html
  index = os.path.join(RESULT_DIR, 'index.html')
  if os.path.exists(index):
    with open(index, 'r') as f:
      data = f.read()
  else:
    data = ''
  with open(index, 'w+') as f:
    f.write(new_row + '\n' + data)
  www_bucket.upload_file(index, 'index.html', ExtraArgs={'ContentType': 'text/html', 'ACL': 'public-read'})


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


all_response = {}
worker_count = {}
start_time = {}

def process_response(response):
  npy_name = response['npy_name']
  img_name = npy_name[:-4]
  top_n = response['top_n']
  worker_id = response['worker_id']
  if npy_name not in all_response:
    all_response[npy_name] = top_n
    worker_count[npy_name] = 1
    start_time[npy_name] = timeit.default_timer()
  else:
    all_response[npy_name] += top_n
    worker_count[npy_name] += 1

  if worker_count[npy_name] >= WORKER_COUNT:
    final_top = sorted(all_response[npy_name],
                       key=lambda kv: -float(kv[1]))[:TOP_N]
    print('{} top results: {}'.format(npy_name, final_top))
    now = timeit.default_timer()
    print('{}: {}secs for top_n'.format(npy_name, now - start_time[npy_name]))
      
    s3_fn = '{}.html'.format(img_name) 
    out_fn = os.path.join(RESULT_DIR, s3_fn)
    with open(out_fn, 'w') as f:
      f.write(result_to_html(final_top, img_name))
    www_bucket.upload_file(
      out_fn, s3_fn,
      ExtraArgs={'ContentType': 'text/html', 'ACL': 'public-read'})
    prepend_to_index(final_top, img_name)
    now = timeit.default_timer()
    print('{}: {}secs for output'.format(npy_name, now - start_time[npy_name]))

    del all_response[npy_name]
    del worker_count[npy_name]
    del start_time[npy_name]

consumer = KafkaConsumer('compare_response',
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))

for msg in consumer:
  process_response(msg.value)
