# N⁴ Matcher (Neural network nearest neighbor matcher)

## Motivation/Application

- Automated image organization
- Stock photograph and video website, make visual content searchable
- Image classification for website with large visual databases
- Image and face recognition on social network 
- Interactive marketing and creative campaigns

## Serving Stack / Pipeline






## Technical Challenge and solution

- For 32x32 image, compare 1 to 1000 takes 1 sec or more
- Use matrix multiplication to become more efficient
- Convert image files to feature vector
- Calculate feature vector for imagenet img (~500x500), 0.8s / file
- Package the vectors and reverse lookup table on server
- Saving (50000, 25000) matrix as npy (s3://ycinsight/50K.tgz)
  Time to load such npy file: 4 seconds
- To compute cosine distance and find top 10:  0.7 seconds
- Serving keras model in lambda

## Nearest Neighbour Search

- Given one image represented by vector with shape of (X), find “nearest” K in N images, each represented as (X)
- Cosine similarity: dot product of (N, X) matrix to (X), the result is an (N) vector
- np.argpartition to find location of top K values
- Combine top M from W workers, then find global top K from W*K results
- Observations:  VGG16 feature is ~70% zeros
- Use scipy.sparse.csr_matrix to speed up calculations
  Perform the same (20000, 25088) dot (25088) 100 times (using real data)
  Sparse dot takes 7.89secs
  Dense dot takes 18.80secs
  A big speed up



