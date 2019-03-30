from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import VGG16
from keras.models import Model
from keras.preprocessing import image
import numpy as np


class FeatureGen(object):
  '''Generate feature for images.'''
  def __init__(self):
    self.load_model()

  def load_model(self):
    self._model = VGG16(weights='imagenet', include_top=False)

  def gen_feature(self, img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = self._model.predict(x)
    return features.reshape([-1])

