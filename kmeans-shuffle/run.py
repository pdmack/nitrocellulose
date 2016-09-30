import argparse
from numpy.random import rand as ra
from functools import reduce
from time import time

from pyspark.sql import SparkSession
from pyspark.mllib.clustering import KMeans

parser = argparse.ArgumentParser()
parser.add_argument('--master', help='Spark master URL (default: "local[*]")', default="local[*]")
parser.add_argument('--size', help='number of macro-records to generate (default: 10000)', default=10000, type=int)
parser.add_argument('--scale', help='number of records per macro-record to generate (default: 100)', default=100, type=int)
parser.add_argument('--dim', help='number of dimensions in each record (default=128)', type=int, default=128)
parser.add_argument('--partitions', help='number of partitions to operate on (default=64)', type=int, default=64)
parser.add_argument('--iterations', help='number of iterations in each training run (default=32)', type=int, default=32)
parser.add_argument('--runs', help='number of training runs (default=10)', type=int, default=10)
parser.add_argument('--clusters', help='number of cluster centers to find (default=128)', type=int, default=128)
parser.add_argument('--config', metavar="KEY=VAL", help="add KEY=VAL to Spark's configuration", action='append', default=[], dest='config')


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    protospark = SparkSession.builder.appName("k-means-gen").master(args.master)
    spark = reduce(lambda x, y: x.config(*y.split("=")), args.config, protospark).getOrCreate()
    rdd = spark.sparkContext.parallelize(range(args.size), args.partitions).flatMap(lambda f: [f] * args.scale).map(lambda x: ra(args.dim))

    runs = args.runs
    clusters = args.clusters
    iterations = args.iterations

    sc = spark.sparkContext
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )

    start_time = time()
    for run in (range(runs)):
        model = KMeans.train(rdd, clusters, iterations)
        rdd.map(lambda l: (model.predict(l), l)).sortByKey().take(args.scale)
    end_time = time()

    sc.stop()

    print("completed %d run%s in %s seconds" % (runs, (runs > 1 and "s" or ""), end_time - start_time))
