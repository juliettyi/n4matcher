from constants import *
from feature import FeatureGen

import json
import numpy
import os


class Matcher(object):
  '''Match feature.'''
  def __init__(self, feature_dir):
    self._feature_dir = feature_dir
    with open(os.path.join(feature_dir, ID_TO_FN)) as f:
      self._id_to_fn = json.load(f)
    with open(os.path.join(feature_dir, FN_TO_ID)) as f:
      self._fn_to_id = json.load(f)
    self._features = numpy.load(FEATURE_FN)
    self._fg = FeatureGen()

  def match(self, feature, top_n=5):
    r = numpy.matmul(self._features, feature)
    print(r.shape)
    r = r.reshape([-1])
    ind = numpy.argpartition(r, -top_n)[-top_n:]
    for i in ind:
      print('{}, score: {}'.format(self._id_to_fn[str(i)], r[i]))

  def match_file(self, fn, top_n=5):
    feature = self._fg.gen_feature(fn)
    self.match(feature, top_n=top_n)
