from flask import current_app as app
from uuid import uuid4
from werkzeug.utils import secure_filename

import boto
import flask
import os
import time
import timeit

ALLOWED_EXTENSIONS = set(['.png', '.jpg', '.jpeg'])

def s3_upload(upload_dir=None, acl='public-read', timeout_per_file=1, max_timeout=5):
    """ Uploads WTForm File Object to Amazon S3

        Expects following app.config attributes to be set:
            S3_KEY              :   S3 API Key
            S3_SECRET           :   S3 Secret Key
            S3_BUCKET           :   What bucket to upload to
            S3_UPLOAD_DIRECTORY :   Which S3 Directory.

        The default sets the access rights on the uploaded file to
        public-read.  It also generates a unique filename via
        the uuid4 function combined with the file extension from
        the source file.
    """

    if upload_dir is None:
        upload_dir = app.config["S3_UPLOAD_DIRECTORY"]
    file_list = flask.request.files.getlist('images')
    file_names = []
    ready = []
    
    conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
    b = conn.get_bucket(app.config["S3_BUCKET"])

    wait_time = min(timeout_per_file * len(file_list), max_timeout)
    for f in file_list:
        source_filename = secure_filename(f.filename)
        source_extension = os.path.splitext(source_filename)[1].lower()
        if source_extension not in ALLOWED_EXTENSIONS:
            print(source_extension, ' not allowed')
            continue
        # destination_filename = source_filename
        destination_filename = uuid4().hex + source_extension
        upload_one_to_s3(b, f, destination_filename, upload_dir, acl)
        file_names.append((source_filename, destination_filename))
        ready.append(False)
    start = timeit.default_timer()
    end = start
    waiting = True
    while waiting and end - start < wait_time:
        waiting = False
        for idx, (_, fn) in enumerate(file_names):
            if not ready[idx]:
                waiting = True
                if check_result(fn):
                    ready[idx] = True
        time.sleep(0.2)
        end = timeit.default_timer()
    # return a list of tuple(source, dest, ready)
    result = [(a,b,c) for ((a,b), c) in zip(file_names, ready)]
    print('upload result: {}'.format(result))
    return result

def upload_one_to_s3(bucket, source_data, s3_dest_name, upload_dir, acl):
    # Connect to S3 and upload file.
    sml = bucket.new_key("/".join([upload_dir, s3_dest_name]))
    sml.set_contents_from_string(source_data.read())
    sml.set_acl(acl)

def check_result(dest_img_file):
    # Check whether html result is ready.
    html_file = dest_img_file + '.html'
    '''EFS is quite slow...
    html_file = os.path.join('/home/ubuntu/efs/matcher', html_file)
    print('checking {}'.format(html_file))
    r = os.path.exists(html_file)
    print('result: {}'.format(r))
    '''
    conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
    b = conn.get_bucket('n4result')
    print('checking {}'.format(html_file))
    key = b.get_key(html_file)
    print('result: ', key)
    return key is not None

