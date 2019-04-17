from constants import *
from feature import FeatureGen
from scipy.sparse import csr_matrix
from scipy.sparse import load_npz

import json
import numpy
import os
import timeit

TEST_IMAGE = 'test.jpg'
BASE = '/home/ubuntu/efs/feature_index/130K_150K/'

fg = FeatureGen()
test = fg.gen_feature(TEST_IMAGE)
print('dense test feature vector shape: {}'.format(test.shape))

with open(os.path.join(BASE, ID_TO_FN)) as f:
  id_to_fn = json.load(f)

print('loading 20K sparse feature index')
start = timeit.default_timer()
sparse = load_npz(os.path.join(BASE, "sparse.npz"))
end = timeit.default_timer()
print('{} secs'.format(end - start))
print('sparse feature vector shape: {}'.format(sparse.shape))

start = timeit.default_timer()
for _ in range(100):
    r = sparse.dot(test)
end = timeit.default_timer()
print('sparse dot {} secs'.format(end - start))
start = timeit.default_timer()
idx = str(numpy.argmax(r))
end = timeit.default_timer()
print('time to calculate argmax {} secs'.format(end - start))

start = timeit.default_timer()
idx1 = numpy.argpartition(r, -10)
end = timeit.default_timer()
print('time to calculate argpartions {} secs'.format(end - start))

start = timeit.default_timer()
idx2 = numpy.argsort(r)
end = timeit.default_timer()
print('time to calculate argsort {}'. format(end - start))

start = timeit.default_timer()
idx3 = sorted(r)
end = timeit.default_timer()
print('time to sort {}'.format(end - start))





print('result is {}'.format(id_to_fn[idx]))

print('loading 20K dense feature index')
start = timeit.default_timer()
dense = numpy.load(os.path.join(BASE, "features.npy"))
end = timeit.default_timer()
print('dense feature vector shape: {}'.format(dense.shape))
print('{} secs'.format(end - start))

start = timeit.default_timer()
for _ in range(100):
    r = numpy.dot(dense, test)
end = timeit.default_timer()
print('result shape {}'.format(r.shape))
idx = str(numpy.argmax(r))
print('dense dot {} secs'.format(end - start))
print('result is {}'.format(id_to_fn[idx]))

