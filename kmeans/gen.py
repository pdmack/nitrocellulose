import argparse
from numpy.random import rand as ra
from functools import reduce
from pyspark.sql import SparkSession


parser = argparse.ArgumentParser()
parser.add_argument('--master', help='Spark master URL (default: "local[*]")', default="local[*]")
parser.add_argument('--outfile', help='where to store example data')
parser.add_argument('--size', help='number of records to generate (default: 100000)', default=1000000, type=int)
parser.add_argument('--dim', help='number of dimensions in each record (default=128)', type=int, default=128)
parser.add_argument('--config', metavar="KEY=VAL", help="add KEY=VAL to Spark's configuration", action='append', default=[], dest='config')


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    protospark = SparkSession.builder.appName("k-means-gen").master(args.master)
    spark = reduce(lambda x, y: x.config(*y.split("=")), args.config, protospark).getOrCreate()
    spark.sparkContext.parallelize(range(args.size)).map(lambda x: ra(args.dim)).saveAsPickleFile(args.outfile)
