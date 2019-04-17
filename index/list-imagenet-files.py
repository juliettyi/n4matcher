import os

IMAGE_DIR = '/home/ubuntu/efs/imagenet/'

# Get all files in training set, that is:
# IMAGE_DIR/xxx/xxx.JPEG

file_list = []
for f in os.listdir(IMAGE_DIR):
    fn = os.path.join(IMAGE_DIR, f)
    # Skip files in main dir, since they are already processed.
    if os.path.isfile(fn):
        continue
    for sub_f in os.listdir(fn):
        sub_fn = os.path.join(fn, sub_f)
        assert os.path.isfile(sub_fn)
        file_list.append(sub_fn)
        if len(file_list) % 1000 == 0:
            print('{} filenames processed.'.format(len(file_list)))
            
fns = sorted(file_list)
with open('imagenet_training_fns.txt', 'w') as f:
    for fn in fns:
        f.write(fn)
        f.write('\n')
