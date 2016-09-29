import argparse

from time import clock

from pyspark.sql import SparkSession
from pyspark.mllib.clustering import KMeans

parser = argparse.ArgumentParser()
parser.add_argument('--master', help='Spark master URL (default: "local[*]")', default="local[*]")

parser.add_argument('--infile', help='where to find input data')
parser.add_argument('--partitions', help='number of partitions to operate on (default=64)', type=int, default=64)
parser.add_argument('--iterations', help='number of iterations in each training run (default=32)', type=int, default=32)
parser.add_argument('--runs', help='number of training runs (default=10)', type=int, default=10)
parser.add_argument('--clusters', help='number of cluster centers to find (default=128)', type=int, default=128)
parser.add_argument('--config', metavar="KEY=VAL", help="add KEY=VAL to Spark's configuration", action='append', default=[], dest='config')


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    protospark = SparkSession.builder.appName("k-means-app").master(args.master)
    spark = reduce(lambda x, y: x.config(*y.split("=")), args.config, protospark).getOrCreate()
    runs = args.runs
    iterations = args.iterations
    partitions = args.partitions
    clusters = args.clusters

    sc = spark.sparkContext
    rdd = sc.pickleFile(args.infile).repartition(partitions)

    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )

    start_time = clock()
    for run in (range(runs)):
        KMeans.train(rdd, clusters, iterations)
    end_time = clock()

    sc.stop()
    
    print("completed %d run%s in %f seconds" % (runs, (runs > 1 and "s" or ""), end_time - start_time))


