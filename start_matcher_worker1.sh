killall -9 python3
nohup python3 -u matcher_worker.py --id=1 --index_names=50K_60K,60K_80K,80K_100K --use_kafka=1 &
tail -f nohup.out
