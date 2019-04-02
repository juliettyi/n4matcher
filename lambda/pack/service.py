import boto3
import numpy
import os
import tempfile
from feature import FeatureGen

s3 = boto3.resource('s3')
fg = FeatureGen()

RESULT_BUCKET = 'dl-result-yc'

def handler(event, context):
  results = []
  for record in event['Records']:
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    print('Image to be processed, from: bucket [%s], object key: [%s]' % (bucket, key))

    # load image
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, 'wb') as f:
      s3.Bucket(bucket).download_file(key, tmp.name)
      tmp.flush()
      feature = fg.gen_feature(tmp.name)
      print('feature generated, size {}'.format(feature.shape))
      numpy.save(tmp.name + '.npy', feature)
      copy_source = {
        'Bucket': bucket,
        'Key': key
      }
      print('sending results to s3')
      s3.meta.client.copy(copy_source, RESULT_BUCKET, key)
      s3.Bucket(RESULT_BUCKET).upload_file(tmp.name + '.npy', key + '.npy')
      print('done')


if __name__ == '__main__':
  event = {
    'Records' : [{
      's3': {
        'bucket': {
          'name': 'deeplearning-test-bucket-lambda18'
        },
        'object': {
          'key': 'IMG_20150121_072954438.jpg'
        }
      }
    }]
  }
  handler(event, None)
