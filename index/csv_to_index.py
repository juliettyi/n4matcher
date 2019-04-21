import csv
import json
import numpy as np
import os
import timeit
import sys

from scipy.sparse import csr_matrix
from scipy.sparse import save_npz
from scipy.sparse import vstack

csv.field_size_limit(sys.maxsize)

ID_TO_FN = 'idx_to_fn.json'
FN_TO_ID = 'fn_to_idx.json'
# FEATURE_FN = 'sparse.npz'

class CsvToIndex(object):
  '''Generate feature for all files under one dir.
  '''
  def __init__(self, csv_file, dest_dir, start=0, end=0):
    self._csv_file = csv_file
    self._dest_dir = dest_dir
    self._start = start
    self._end = end    

  def gen_features(self):
    # features = []
    sparse_features = []
    idx_to_fn = {}
    fn_to_idx = {}
    starttime = timeit.default_timer()
    with open(self._csv_file, 'r') as f1:
      f1_reader = csv.reader(f1, delimiter='\t')
      row_count = 0
      for row in f1_reader:
        if row_count >= self._start and row_count < self._end:
          idx = row_count - self._start
          if row[1] == 'ERROR':
            continue
          feature = np.array(json.loads(row[1]))
          # features.append(feature)
          sparse_feature = csr_matrix(feature)
          sparse_features.append(sparse_feature)
          f = row[0].replace('/home/ubuntu/efs/imagenet/', '')
          idx_to_fn[idx] = f
          fn_to_idx[f] = idx
          if idx % 10000 == 0:
            now = timeit.default_timer()
            print('{} rows processed, time: {}'.format(idx, now - starttime))        
            # print('{} files processed'.format(len(self._fn_list)))
        row_count += 1
        if self._end != 0 and row_count >= self._end:
          break  
      with open(os.path.join(self._dest_dir, ID_TO_FN), 'w') as f:
        json.dump(idx_to_fn, f)
      with open(os.path.join(self._dest_dir, FN_TO_ID), 'w') as f:
        json.dump(fn_to_idx, f)
      # features = np.stack(features, axis=0)
      # sparse = csr_matrix(features)
      sparse_2 = vstack(sparse_features)
      # print((sparse != sparse_2).nnz==0)
      # print('feature shape = ', features.shape)
      print(self._dest_dir, sparse_2.shape)
      # numpy.save(FEATURE_FN, features)
      save_npz(os.path.join(self._dest_dir, 'sparse'), sparse_2)
'''
csv_to_index = CsvToIndex('/home/ubuntu/efs/feature_index/dbcsv/vgg16v1.csv',
  	                  './', start=0, end=50)
csv_to_index.gen_features()
'''

list_of_generators = []
'''
list_of_generators.append(
  CsvToIndex('/home/ubuntu/efs/feature_index/dbcsv/vgg16v1.csv',
             '/home/ubuntu/efs/feature_index/150K_200K', start=0, end=50000))
'''
list_of_generators.append(
  CsvToIndex('/home/ubuntu/efs/feature_index/dbcsv/vgg16v1.csv',
             '/home/ubuntu/efs/feature_index/200K_250K', start=50000, end=100000))
list_of_generators.append(
  CsvToIndex('/home/ubuntu/efs/feature_index/dbcsv/vgg16v1.csv',
             '/home/ubuntu/efs/feature_index/250K_300K', start=100000, end=150000))
list_of_generators.append(
  CsvToIndex('/home/ubuntu/efs/feature_index/dbcsv/vgg16v2.csv',
             '/home/ubuntu/efs/feature_index/300K_350K', start=0, end=50000))
list_of_generators.append(
  CsvToIndex('/home/ubuntu/efs/feature_index/dbcsv/vgg16v2.csv',
             '/home/ubuntu/efs/feature_index/350K_400K', start=50000, end=100000))
list_of_generators.append(
  CsvToIndex('/home/ubuntu/efs/feature_index/dbcsv/vgg16v2.csv',
             '/home/ubuntu/efs/feature_index/400K_450K', start=100000, end=150000))
for csv_to_index in list_of_generators:
  csv_to_index.gen_features()
