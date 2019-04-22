This directory is a self-contained code base for MVP demo,
which load an small index of 1000 images, generate feature for all images under test_imgs,
send them to matcher and get top 10 matches.

Github requires file size less than 100MB, so my original plan of using a big index 
for 50K images did not pass (the index size is ~800MB)


To run the MVP demo:

pip3 install -r requirements.txt
python3 main.py

