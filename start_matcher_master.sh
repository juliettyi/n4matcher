killall -9 python3
nohup python3 -u matcher_master.py &
nohup python3 -u matcher_reducer.py &
tail -f nohup.out
