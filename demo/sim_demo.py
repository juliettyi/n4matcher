import imageio
import math
import numpy
import os
import sys
import timeit

from scipy import misc
from scipy import spatial
from skimage.measure import compare_ssim


IMAGE_BASE = '/home/ubuntu/artificio/similar_images_TL/db'
IMAGE_SIZE = 100
TOP_N = 3

file_list = os.listdir(IMAGE_BASE)
fn_list = []
for fn in file_list:
    if 'resize' not in fn:
        continue
    fn_list.append(fn)
fn_list = sorted(fn_list)


def load_image(img_id):
    fn = os.path.join(IMAGE_BASE, img_id)
    image = imageio.imread(fn).astype(numpy.float32)
    image = numpy.reshape(image, [IMAGE_SIZE * IMAGE_SIZE * 3])
    return image

def consine_dist(img1, img2):
    def L2_normalize(image):
        # convert to unit vector by L2 norm
        r = image / math.sqrt(numpy.linalg.norm(image, ord=2))
        return r

    img1 = L2_normalize(img1)
    img2 = L2_normalize(img2)
    return spatial.distance.cosine(img1, img2)

def mse(img1, img2):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    return numpy.mean((img1.astype("float") - img2.astype("float")) ** 2)

def compare_images(img1, img2):
    return (consine_dist(img1, img2),
            mse(img1, img2),
            compare_ssim(img1, img2))

def print_result(kv):
    target = kv[0]
    scores = kv[1]
    print('http://35.167.117.254/efs/sampleimage/{}'.format(target), scores)

def compare_many(fn_list):
    start = timeit.default_timer()

    for src in fn_list:
        scores = {}
        img1 = load_image(src)
        for target in fn_list:
            img2 = load_image(target)
            dist_measures = compare_images(img1, img2)
            scores[target] = dist_measures
    
        # 0 means perfect match
        sorted_by_cosine_dist = sorted(scores.items(), key=lambda kv: kv[1][0])
        # 0 means perfect match
        sorted_by_mse = sorted(scores.items(), key=lambda kv: kv[1][1])
        # ssim: higher means more similar, 1 means perfect match
        sorted_by_ssim = sorted(scores.items(), key=lambda kv: -kv[1][2])

        print('src = {}'.format(src))
        print('by costine distance')
        for kv in sorted_by_cosine_dist[:TOP_N]:
            print_result(kv)
        print('by mean squared error')
        for kv in sorted_by_mse[:TOP_N]:
            print_result(kv)
        print('by structrual sim')
        for kv in sorted_by_ssim[:TOP_N]:
            print_result(kv)
    
    stop = timeit.default_timer()
    print('time: {} secs, compared {} images'.format(stop - start, len(fn_list) * len(fn_list)))

    
TEST_MODE = False

if TEST_MODE:
    def compare(id1, id2):
        img1 = load_image(id1)
        img2 = load_image(id2)
        # print(img1.tolist())
        # print(img2.tolist())
        return compare_images(img1, img2)
    print(compare('asparagus1_resized.jpeg', 'asparagus1_resized.jpeg'))
    print(compare('asparagus1_resized.jpeg', 'asparagus2_resized.jpg'))
else:
    compare_many(fn_list)

