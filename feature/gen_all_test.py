from gen_all import GenAll

import argparse

parser = argparse.ArgumentParser(description='GenAll')
parser.add_argument('--start', type=int, default=0, help='start position')
parser.add_argument('--end', type=int, default=-1, help='end position, -1 means everything')

args = parser.parse_args()
print('Processing files in [{}, {}]'.format(args.start, args.end))

ga = GenAll('/home/ubuntu/efs/imagenet/', start=args.start, end=args.end)
ga.gen_features()
