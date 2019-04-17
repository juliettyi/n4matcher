from feature import FeatureGen
from keras.applications.vgg16 import VGG16
from spark_gen import featurize
from spark_gen import convert_to_str
from spark_gen import load_from_str

import json
import numpy
import pickle

model = VGG16(weights='imagenet', include_top=False)
fg = FeatureGen(model)

# dirty input
print(convert_to_str(featurize(fg, '/home/ubuntu/efs/imagenet/n01580077/n01580077_7373.JPEG.CAf2d8b5')))
# clean input
feature_vector = featurize(fg, '/home/ubuntu/efs/imagenet/n01580077/n01580077_999.JPEG')
print(type(feature_vector))
print(feature_vector.shape)
feature_str = convert_to_str(feature_vector)
print(len(feature_str))
print(feature_str[:100])
# deserialize
feature = load_from_str(feature_str)
print(type(feature))
print(feature.shape)
print(feature)
