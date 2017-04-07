package radanalyticsio.sombench

import org.apache.spark.sql.SparkSession
import scopt.OptionParser

case class SOMConfig(cores: Option[Int] = None, partitionCount: Int = (2 << 7), featureCount: Int = (2 << 7), recordCount: Int = (2 << 20), seed: Int = 0xdea110c8, logdir: Option[String] = None)

object Main {
  import org.apache.spark.mllib.linalg.{DenseVector => DV}
  import com.redhat.et.silex.som.SOM
  
  def main(args: Array[String]) {
    
    val parser = new OptionParser[SOMConfig]("sombench") {
      head("sombench", "0.0.1")

      opt[Int]("cores")
	.action((x,c) => c.copy(cores=Some(x)))
	.text("number of cores to use (default: all available cores)")

      opt[Int]('p', "partitions")
	.action((x,c) => c.copy(partitionCount=x))
	.text("number of partitions to create (default: 256)")

      opt[Int]('f', "features")
	.action((x,c) => c.copy(featureCount=x))
	.text("number of features per vector (default: 256)")

      opt[Int]('c', "record-count")
	.action((x,c) => c.copy(recordCount=x))
	.text("number of records (default: 2^20)")

      opt[Int]('s', "seed")
	.action((x,c) => c.copy(seed=x))
	.text("seed for random data generator (default is hardcoded)")

      opt[String]("logdir")
	.action((x, c) => c.copy(logdir=Some(x)))
	.text("collect spark history logs in specified dir (default:  don't collect logs)")

      help("help").text("prints this usage text")
    }
    
    parser.parse(args, SOMConfig()) match {
      case Some(config) =>
	val master = config.cores.map(c => s"local[$c]").getOrElse("local[*]")
	val basicSesh = SparkSession.builder().master(master)

	val sesh = config.logdir.flatMap { dir =>
	  val fpath = new java.io.File(dir)

	  (fpath.exists() || fpath.mkdirs()) match {
	    case true =>
	      val realpath = fpath.toPath().toRealPath().toString()
	      Some(basicSesh.config("spark.eventLog.enabled", "true").config("spark.eventLog.dir", s"file://$realpath"))
	    case false =>
	      Console.println(s"warning:  can't create dir $dir; won't record event log")
	      None
	  }
	}.getOrElse(basicSesh).getOrCreate()
	
	val sc = sesh.sparkContext
	
	val partitions = config.partitionCount
	val records = config.recordCount / partitions
	val features = config.featureCount
	val rnd = new scala.util.Random(config.seed) 

	val exampleSeeds = sc.parallelize(Array.fill(partitions)(rnd.nextInt)).repartition(partitions)
	val examples = exampleSeeds.flatMap { s => { val r = new scala.util.Random(s); Array.fill(records)(new DV(Array.fill(features)(r.nextDouble)).compressed) } }
	
	val t_start = System.nanoTime()
	SOM.train(24, 24, features, 20, examples, sigmaScale=0.7)      
	val t_end = System.nanoTime()

	sc.stop()
	
	println("Elapsed time was " + (t_end - t_start) + "ns")
      case None => ()
    }
  }
}
