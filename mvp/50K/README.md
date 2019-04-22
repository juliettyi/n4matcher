Since original sparse.npz is ~800MB, I used split to break it uo into pieces so that they can be uploaded to github.

to split:

spilt --bytes=90M sparse.npz

to combine:

cat x* > sparse.npz
