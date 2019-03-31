import boto3
import os
import tempfile
from feature import FeatureGen

s3 = boto3.resource('s3')
fg = FeatureGen()

def handler(event, context):
    results = []
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        print('Running Deep Learning example using Tensorflow library ...')
        print('Image to be processed, from: bucket [%s], object key: [%s]' % (bucket, key))

        # load image
        tmp = tempfile.NamedTemporaryFile()
        with open(tmp.name, 'wb') as f:
            s3.Bucket(bucket).download_file(key, tmp.name)
            tmp.flush()
            feature = fg.gen_feature('tmp.name')
            print(feature.shape)
