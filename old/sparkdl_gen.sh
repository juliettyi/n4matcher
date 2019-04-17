# PYSPARK_PYTHON=python3 spark-submit --packages databricks:tensorframes:0.6.0-s_2.11,databricks:spark-deep-learning:1.2.0-spark2.3-s_2.11,org.postgresql:postgresql:42.1.1 --master spark://10.0.0.7:7077 --executor-memory 6G sparkdl_gen.py
PYSPARK_PYTHON=python3 spark-submit --packages databricks:tensorframes:0.6.0-s_2.11,databricks:spark-deep-learning:1.2.0-spark2.3-s_2.11,org.postgresql:postgresql:42.1.1 --master local[*] --executor-memory 6G \
--conf "spark.dynamicAllocation.enable=true" \
--conf "spark.dynamicAllocation.executorIdleTimeout=2m" \
--conf "spark.dynamicAllocation.minExecutors=1" \
--conf "spark.dynamicAllocation.maxExecutors=2000" \
--conf "spark.stage.maxConsecutiveAttempts=10" \
--conf "spark.memory.offHeap.enable=true" \
--conf "spark.memory.offHeap.size=3g" \
--conf "spark.yarn.executor.memoryOverhead=0.1 * (spark.executor.memory + spark.memory.offHeap.size)" \
--conf "spark.shuffle.file.buffer=1m" \
--conf "spark.executor.extraJavaOptions=-XX:ParallelGCThreads=4 -XX:+UseParallelGC" \
--conf "spark.shuffle.service.index.cache.size=2048" \
--conf "spark.shuffle.registration.timeout=2m" \
--conf "spark.shuffle.registration.maxAttempts=5" \
sparkdl_gen.py
