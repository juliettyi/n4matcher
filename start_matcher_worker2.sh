killall -9 python3
nohup python3 -u matcher_worker.py --id=2 --index_names=300K_350K,350K_400K,400K_450K &
tail -f nohup.out
