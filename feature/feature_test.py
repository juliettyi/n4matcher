from feature import FeatureGen

import numpy as np
import os
import timeit

fg = FeatureGen()

def batch_size_1():
  start = timeit.default_timer()
  feature = fg.gen_feature(os.path.join('test_imgs', '00001.png'))
  print(feature.shape)
  print('array: ', np.array2string(feature))
  now = timeit.default_timer()
  print('{} secs'.format(now - start))

def batch_size_2():
  start = timeit.default_timer()
  x1 = fg.load_img(os.path.join('test_imgs', '00001.png'))
  x2 = fg.load_img(os.path.join('test_imgs', '00002.png'))
  x = np.stack([x1, x2], axis=0)
  features = fg.gen_feature_for_batch(x)
  print(features.shape)
  now = timeit.default_timer()
  print('{} secs'.format(now - start))

def many_files():
  start = timeit.default_timer()
  fn_list = [
      os.path.join('test_imgs', '00001.png'),
      os.path.join('test_imgs', '00002.png'),
      os.path.join('test_imgs', '00003.png'),
      os.path.join('test_imgs', '00004.png')
      ]
  features = fg.gen_n_features(fn_list)
  print(features.shape)
  now = timeit.default_timer()
  print('{} secs'.format(now - start))

def read_files():
  fn_list = [
      os.path.join('test_imgs', '00001.png'),
      os.path.join('test_imgs', '00002.png'),
      os.path.join('test_imgs', '00003.png'),
      os.path.join('test_imgs', '00004.png')
      ]
  for fn in fn_list:
    start = timeit.default_timer()
    content = fg.load_img(fn)
    now = timeit.default_timer()
    print('{} secs'.format(now - start))

def batch_size():
  fn_list = [
      os.path.join('test_imgs', '00001.png'),
      os.path.join('test_imgs', '00002.png'),
      os.path.join('test_imgs', '00003.png'),
      os.path.join('test_imgs', '00004.png')
      ]
  c = []
  for fn in fn_list:
    start = timeit.default_timer()
    content = fg.load_img(fn)
    now = timeit.default_timer()
    print('{} secs'.format(now - start))
    c.append(content)

  for _ in range(5):
    c += c
    start = timeit.default_timer()
    f = fg.gen_feature_for_batch(np.stack(c, axis=0))
    print(f.shape)
    now = timeit.default_timer()
    print('batch size: {}, {} secs'.format(len(c), now - start))
    
  

read_files()
batch_size_1()
batch_size_2()
many_files()
batch_size()
