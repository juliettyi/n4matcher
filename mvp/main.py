from feature import FeatureGen
from matcher import Matcher

import os
import timeit

print('Loading feature index for 50,000 images, please wait...')
start = timeit.default_timer()
m = Matcher('./50K/')
fg = FeatureGen()
end = timeit.default_timer()
index_load_time = end - start
print('Index loaded, time used = {} seconds'.format(index_load_time))

test_imgs = os.listdir('./test_imgs')
file_count = len(test_imgs)
print('Generating features for {} images in ./test_imgs'.format(file_count))
features = {}
start = timeit.default_timer()
for fn in test_imgs:
  feature_for_fn = fg.gen_feature(os.path.join('./test_imgs', fn))
  features[fn] = feature_for_fn
end = timeit.default_timer()
feature_time = end - start
print('generated features for {} files, time used = {} seconds'.format(file_count, feature_time))

start = timeit.default_timer()
for test_img_fn in features:
  print('matching {}'.format(test_img_fn))
  top = m.match(features[test_img_fn], top_n=10)
  # sort top 10
  top_sorted = sorted(top.items(), key=lambda kv:-kv[1])
  for matched_fn,score in top_sorted:
    print('https://s3-us-west-2.amazonaws.com/yc-insight-imagenet/{}, score:{}'.format(matched_fn, score))
end = timeit.default_timer()

print('index loaded, time used = {} seconds'.format(index_load_time))
print('generated features for {} files, time used = {} seconds'.format(file_count, feature_time))
print('matched {} files, time used = {} seconds'.format(file_count, end - start))
