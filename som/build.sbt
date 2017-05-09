name := "sombench"

organization := "radanalyticsio"

version := "0.0.1"

scalaVersion := "2.11.8"

val SPARK_VERSION = "2.1.0"
val SCALA_VERSION = "2.11.8"

resolvers += "Will's bintray" at "https://dl.bintray.com/willb/maven/"

def commonSettings = Seq(
  libraryDependencies ++= Seq(
    "com.github.scopt" %% "scopt" % "3.5.0",
    "org.apache.spark" %% "spark-core" % SPARK_VERSION % "provided",
    "org.apache.spark" %% "spark-sql" % SPARK_VERSION % "provided",
    "org.apache.spark" %% "spark-mllib" % SPARK_VERSION % "provided",
    "org.scala-lang" % "scala-reflect" % SCALA_VERSION % "provided",
    "com.redhat.et" %% "silex" % "0.1.1"
  )
)

seq(commonSettings:_*)

licenses += ("Apache-2.0", url("http://opensource.org/licenses/Apache-2.0"))

scalacOptions ++= Seq("-unchecked", "-deprecation", "-feature")

scalacOptions in (Compile, doc) ++= Seq("-doc-root-content", baseDirectory.value+"/root-doc.txt")

(dependencyClasspath in Test) <<= (dependencyClasspath in Test).map(
  _.filterNot(_.data.name.contains("slf4j-log4j12"))
)

lazy val es2parquet = (project in file(".")).
  settings(commonSettings: _*)
