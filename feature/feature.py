from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import VGG16
from keras.models import Model
# This introduces dependencies on scipy, which is VERY hard to support by lambda.
# from keras.preprocessing import image
import image
import math
import numpy as np


def get_feature(model, x):
  '''get feature from model(x).'''
  def L2_normalize(f):
    # convert to unit vector by L2 norm
    return f / math.sqrt(np.linalg.norm(f.reshape(-1), ord=2))
  return L2_normalize(model.predict(x))


class FeatureGen(object):
  '''Generate feature for images.'''
  def __init__(self, model=None):
    if not model:
      self.load_model()
    else:
      self._model = model

  def load_model(self):
    self._model = VGG16(weights='imagenet', include_top=False)

  def load_img(self, img_path):
    '''Load one image.'''
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    return x
  
  def gen_feature(self, img_path):
    '''Generate feature for one image.'''
    x = self.load_img(img_path)
    # simulate batch size of 1
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = get_feature(self._model, x)
    return features.reshape(-1)

  def gen_n_features(self, img_paths):
    '''Generate feature for many images at the same time.'''
    x_list = []
    for img_p in img_paths:
      x = self.load_img(img_p)
      x_list.append(x)
    x = np.stack(x_list, axis=0)
    return self.gen_feature_for_batch(x)

  def gen_feature_for_batch(self, inp):
    x = preprocess_input(inp)
    features = get_feature(self._model, x)
    return features.reshape([features.shape[0], -1])


