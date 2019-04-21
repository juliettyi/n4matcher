killall -9 python3
nohup python3 -u matcher_worker.py --id=1 --index_names=150K_200K,200K_250K,250K_300K &
tail -f nohup.out
