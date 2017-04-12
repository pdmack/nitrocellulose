# sombench

This is a simple application that uses the [self-organizing map](https://en.wikipedia.org/wiki/Self-organizing_map) code from [Silex](https://silex.freevariable.com) as a benchmark workload.

# Building

Run `./sbt assembly`.

# Running

Run `java -jar target/scala-2.11/sombench-assembly-0.0.1.jar --help` for usage instructions.  The default workload size should be runnable on a recent laptop.  To really exercise the heap, you'll want to run a larger problem size.  The interesting dimensions are:

    * `--cores` -- use this to limit cores devoted to Spark executors (if you have, e.g., hyperthreading enabled)
    * `--partitions` -- use this to limit the amount of work in any single task.  More partitions means smaller tasks.
    * `--record-count` -- use this to specify the number of records in the training set.  The default is 2^20; an interesting real-world application might be on the order of 10^8 records or so.
    * `--features` -- use this to increase the size of each record (and thus change the tradeoffs between total heap usage and per-object overhead).  Realistic values probably fall within the range of 2^4 -- 2^12 or so.

# Interpreting results

The program will give you a timing for the SOM training step itself.  If you've run it with the `--logdir` option, there will also be a JSON file with Spark metric events (including individual task wall, CPU, and GC times) in that directory.  For an example of how to postprocess those results using Spark, see the [`metrics` subdirectory](../metrics/metrics.ipynb) of this repository.