import imageio
import math
import numpy
import os
from scipy import misc
from scipy import spatial
from skimage.measure import compare_ssim
import timeit


IMAGE_BASE = '/home/ubuntu/data/imagenet/valid_32x32'
IMAGE_SIZE = 32
NUM_TARGETS = 1000


def load_image(img_id):
    fn = os.path.join(IMAGE_BASE, img_id + '.png')
    image = imageio.imread(fn).astype(numpy.float32)
    image = numpy.reshape(image, [IMAGE_SIZE * IMAGE_SIZE * 3])
    return image

def consine_dist(img1, img2):
    def L2_normalize(image):
        # convert to unit vector by L2 norm
        r = image / math.sqrt(numpy.linalg.norm(image, ord=2))
        return r

    n_img1 = L2_normalize(img1)
    n_img2 = L2_normalize(img2)
    return spatial.distance.cosine(n_img1, n_img2)

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
    print('http://35.167.117.254/efs/imagenet_small/valid_32x32/{}.png'.format(target), scores)

def compare_many(src, num_targets=NUM_TARGETS):
    start = timeit.default_timer()
    scores = {}
    id1 = '%.5d' % src
    img1 = load_image(id1)

    for target in range(1, num_targets):
        id2 = '%.5d' % target
        img2 = load_image(id2)
        dist_measures = compare_images(img1, img2)
        scores[id2] = dist_measures
    
    stop = timeit.default_timer()
    # 0 means perfect match
    sorted_by_cosine_dist = sorted(scores.items(), key=lambda kv: kv[1][0])
    # 0 means perfect match
    sorted_by_mse = sorted(scores.items(), key=lambda kv: kv[1][1])
    # ssim: higher means more similar, 1 means perfect match
    sorted_by_ssim = sorted(scores.items(), key=lambda kv: -kv[1][2])

    print('by costine distance')
    for kv in sorted_by_cosine_dist[:10]:
        print_result(kv)
    print('by mean squared error')
    for kv in sorted_by_mse[:10]:
       print_result(kv)
    print('by structrual sim')
    for kv in sorted_by_ssim[:10]:
       print_result(kv)
    print('time: {} secs, compared {} images'.format(stop - start, NUM_TARGETS))

    
TEST_MODE = False

if TEST_MODE:
    def compare(id1, id2):
        img1 = load_image(id1)
        img2 = load_image(id2)
        # print img1
        # print img2
        return compare_images(img1, img2)
    print(compare('00001', '00001'))
    print(compare('00001', '00002'))
else:
    # use image 1 as source.
    compare_many(src=1)

