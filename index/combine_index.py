'''Combine multiple feature index into single feature index.'''
from scipy.sparse import csr_matrix
from scipy.sparse import load_npz
from scipy.sparse import save_npz
from scipy.sparse import vstack

import json
import numpy
import sys
import os
# workaround import from sibling dir
sys.path.append(os.path.abspath('../feature'))
from constants import *
from matcher import Matcher


class FeatureCombiner(object):
  def __init__(self, base_dir, feature_dir_list, combined_dir):
    self._index_list = []
    for feature_dir in feature_dir_list:
      feature_dir = os.path.join(base_dir, feature_dir)
      print('join feature_dirs {}'.format(feature_dir))
      self._index_list.append(Matcher(feature_dir))
    self._combined_dir = os.path.join(base_dir, combined_dir)
    print('into {}'.format(self._combined_dir))
    if not os.path.exists(self._combined_dir):
      os.mkdir(self._combined_dir)

  def combine(self):
    combined_id_to_fn = {}
    combined_fn_to_id = {}
    id_offset = 0
    npz_list = []
    for index in self._index_list:
      npz_list.append(index._features)
      for k in index._id_to_fn:
        combined_id_to_fn[str(int(k) + id_offset)] = index._id_to_fn[k]
      for k in index._fn_to_id:
        combined_fn_to_id[k] = str(int(index._fn_to_id[k]) + id_offset)
      id_offset += len(index._id_to_fn)
    combined_index = vstack(npz_list)
      
    print('new id_to_fn: {}'.format(len(combined_id_to_fn)))
    with open(os.path.join(self._combined_dir, ID_TO_FN), 'w') as f:
      json.dump(combined_id_to_fn, f)
    print('new fn_to_id: {}'.format(len(combined_fn_to_id)))
    with open(os.path.join(self._combined_dir, FN_TO_ID), 'w') as f:
        json.dump(combined_fn_to_id, f)
    print('new index shape: {}'.format(combined_index.shape))
    save_npz(os.path.join(self._combined_dir, 'sparse'), combined_index)
          

BASE = '/home/ubuntu/efs/feature_index'

'''
combiner1 = FeatureCombiner(BASE, ['0K_10K', '10K_30K', '30K_50K'], '0K_50K')
combiner1.combine()

combiner2 = FeatureCombiner(BASE, ['50K_60K', '60K_80K', '80K_100K'], '50K_100K')
combiner2.combine()

combiner3 = FeatureCombiner(BASE, ['100K_110K', '110K_130K', '130K_150K'], '100K_150K')
combiner3.combine()
'''

# Memory error when stacking these 3.
# combiner4 = FeatureCombiner(BASE, ['0K_50K', '50K_100K', '100K_150K'], '0K_150K')
# combiner4.combine()

combiner5 = FeatureCombiner(BASE, ['0K_50K', '50K_100K'], '0K_100K')
combiner5.combine()
