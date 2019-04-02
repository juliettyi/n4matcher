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
import tempfile
import time

from kafka import KafkaProducer

IN_BUCKET = 'dl-result-yc'
OUT_BUCKET = 'dl-results-final'
SRC_BUCKET = 'yc-insight-imagenet'
WORKER_COUNT = 3
TOP_N = 10

# Producer, using json format for serialization.
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Keep monitoring the bucket
s3 = boto3.resource('s3')
in_bucket = s3.Bucket(IN_BUCKET)
out_bucket = s3.Bucket(OUT_BUCKET)

def prepend_to_index(r, img_name, img_result_fn):
  new_row = result_to_row(r, img_name, img_result_fn)

  # save html
  index = 'index.html'
  tmp_html = tempfile.NamedTemporaryFile()
  with open(tmp_html.name, 'w') as f:
    f.write(new_row)

    old_html = tempfile.NamedTemporaryFile()
    out_bucket.download_file(index, old_html.name)
    with open(old_html.name, 'r') as f2:
      f.write(f2.read())
    
  out_bucket.upload_file(tmp_html.name, index)
  

def result_to_row(r, img_name, img_result_fn):
  line = ['<table><tr>']
  # self.
  link = 'http://{}.s3-website-us-west-2.amazonaws.com/{}'.format(OUT_BUCKET, img_result_fn)
  line.append('<td><a href={}><img class=row_img height=256 width=256 src="https://s3-us-west-2.amazonaws.com'
                '/{}/{}" /></a></td>'.format(link, OUT_BUCKET, img_name))
  # top similar images
  for name,score in r:
    line.append('<td><img class=row_img height=256 width=256 src="https://s3-us-west-2.amazonaws.com'
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
  
  out_fn = '{}.html'.format(img_name)
  # save html
  tmp_html = tempfile.NamedTemporaryFile()
  with open(tmp_html.name, 'w') as f:
    f.write(result_to_html(final_top, img_name))
  out_bucket.upload_file(tmp_html.name, out_fn)
  prepend_to_index(final_top, img_name, out_fn)
  print('Uploaded to {}/{}'.format(OUT_BUCKET, out_fn))

  
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


print('started...')
while True:
  process_bucket()
  time.sleep(1)
