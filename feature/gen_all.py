import json
import numpy
import os
import timeit
from constants import *
from feature import FeatureGen

class GenAll(object):
  '''Generate feature for all files under one dir.
  '''
  def __init__(self, src_dir, start=0, end=0):
    self._src_dir = src_dir
    all_fn = os.listdir(src_dir)
    self._fn_list = sorted([f for f in all_fn if os.path.isfile(os.path.join(src_dir, f))])
    # take range if specified.
    if start > 0 or end > 0:
      if end > 0:
        self._fn_list = self._fn_list[start:end]
      else:
        self._fn_list = self._fn_list[start:]
    self._fg = FeatureGen()

  def gen_features(self):
    features = []
    idx_to_fn = {}
    fn_to_idx = {}
    start = timeit.default_timer()
    print('{} files to process'.format(len(self._fn_list)))
    for idx, f in enumerate(self._fn_list):
      feature = self._fg.gen_feature(os.path.join(self._src_dir, f))
      features.append(feature)
      idx_to_fn[idx] = f
      fn_to_idx[f] = idx
      if idx % 10 == 0:
        now = timeit.default_timer()
        print('{} files processed, time: {}'.format(idx, now - start))        
    print('{} files processed'.format(len(self._fn_list)))
    with open(ID_TO_FN, 'w') as f:
        json.dump(idx_to_fn, f)
    with open(FN_TO_ID, 'w') as f:
        json.dump(fn_to_idx, f)
    features = numpy.stack(features, axis=0)
    print(features.shape)
    numpy.save(FEATURE_FN, features)

