# from constants import *
from scipy.sparse import csr_matrix
from scipy.sparse import save_npz

import json
import numpy
import os


class Sparsify(object):
  def __init__(self, feature_dir):
    self._feature_dir = feature_dir
    self._features = numpy.load(os.path.join(feature_dir, 'features.npy'))

  def sparsify(self):
    print('sparsify {}'.format(self._features.shape))
    sparse = csr_matrix(self._features)
    print('shape {}'.format(sparse.shape))
    save_npz(os.path.join(self._feature_dir, "sparse"), sparse)


# BASE = '/home/ubuntu/efs/feature_index'
BASE = './'
for d in os.listdir(BASE):
  full_path = os.path.join(BASE, d)
  if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, 'features.npy')):
    print('fixing {}'.format(d))
    fix = Sparsify(full_path)
    fix.sparsify()
