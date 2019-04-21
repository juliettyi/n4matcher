killall -9 python3
nohup python3 -u matcher_worker.py --id=0 --index_names=0K_50K,50K_100K,100K_150K &
tail -f nohup.out
