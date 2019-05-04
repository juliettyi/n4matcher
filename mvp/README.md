This directory is a self-contained code base for MVP demo,
which load an index of 50000 images, generate feature for all images under test_imgs,
send them to matcher and get top 10 matches.

To run the MVP demo:

One time setup:

sudo apt-get update

sudo apt-get -y install python3-pip

pip3 install -r requirements.txt


cd 50K


cat x* > sparse.npz

Run mvp demo:

cd ..

python3 main.py



An sample output from an aws t2.small EC2:

index loaded, time used = 15.98753700500015 seconds

generated features for 15 files, time used = 13.173495285000172 seconds

matched 15 files, time used = 3.0983668599997145 seconds
