killall -9 python3
nohup python3 -u matcher_worker.py --id=2 --index_names=100K_150K --use_kafka=1 &
tail -f nohup.out
