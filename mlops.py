# -*- coding: utf-8 -*-
"""MLOPS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ecBFrs7XZw09xVmX4526Wnn1Exw5B04h
"""

#Cloudera 

MLOPS pipeline with spark streaming and Kafka on cloudera

from pyspark.sql.functions import from_json, col, explode
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
import mlflow
from datetime import datetime, timedelta
Define constants
SPARK_APP_NAME = "MLOps-Spark-Streaming-Kafka"
SPARK_MASTER = "local[*]"
SPARK_BATCH_INTERVAL = 1800  # 30 minutes
MODEL_PATH = "/path/to/model"
FEATURE_COLUMNS = ["feature1", "feature2", "feature3", "feature4"]
KAFKA_BOOTSTRAP_SERVERS = "kafka-broker1:9092,kafka-broker2:9092"
KAFKA_TOPIC = "my-topic"
KAFKA_STARTING_OFFSETS = "earliest"
KAFKA_CHECKPOINT_LOCATION = "/path/to/checkpoint"
Define schema for incoming Kafka messages
kafka_schema = StructType([
    StructField("label", DoubleType()),
    StructField("feature1", DoubleType()),
    StructField("feature2", DoubleType()),
    StructField("feature3", DoubleType()),
    StructField("feature4", DoubleType())
])
Create Spark session
spark = SparkSession.builder \
    .appName(SPARK_APP_NAME) \
    .master(SPARK_MASTER) \
    .getOrCreate()
Create MLflow experiment
mlflow.set_experiment("MLOps-Spark-Streaming-Kafka")
Define Kafka data stream source and preprocessing
raw_stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", KAFKA_STARTING_OFFSETS) \
    .load()
preprocessed_stream = raw_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), kafka_schema).alias("json")) \
    .select("json.*")
Define model training function
def train_model():
    with mlflow.start_run():
        # Define model and training parameters
        lr = LogisticRegression()
        assembler = VectorAssembler(inputCols=FEATURE_COLUMNS, outputCol="features")
        evaluator = BinaryClassificationEvaluator()
        # Split preprocessed data into training and testing sets
        train_data, test_data = preprocessed_stream.randomSplit([0.7, 0.3], seed=123)
        # Assemble feature vector
        train_data = assembler.transform(train_data).select("features", "label")
        test_data = assembler.transform(test_data).select("features", "label")
        # Train model
        model = lr.fit(train_data)
        # Evaluate model
        auc = evaluator.evaluate(model.transform(test_data))
        mlflow.log_metric("auc", auc)
        # Save model
        model.write().overwrite().save(MODEL_PATH)
        mlflow.log_artifact(MODEL_PATH, "model")
Define streaming query and start it
training_query = preprocessed_stream.writeStream \
    .trigger(processingTime=f"{SPARK_BATCH_INTERVAL} seconds") \
    .option("checkpointLocation", KAFKA_CHECKPOINT_LOCATION) \
    .foreachBatch(lambda batch_df, batch_id: train_model()) \
    .start()
Wait for the query to terminate
training_query.awaitTermination()

we read streaming data from Kafka and preprocess it using a specified schema. We then define a training function that trains

Code for an MLOps pipeline which reads a Kafka topic into Spark structured streaming, performs classification with a classification model, and then writes the output to a new Kafka topic every 30 minutes

from pyspark.sql.functions import from_json, col, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from kafka import KafkaProducer
from datetime import datetime, timedelta
Define constants
APP_NAME = "MLOps-Kafka-Spark-Streaming"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
INPUT_TOPIC = "input-topic"
OUTPUT_TOPIC = "output-topic"
BATCH_DURATION = 1800  # 30 minutes
MODEL_PATH = "/path/to/model"
FEATURE_COLUMNS = ["feature1", "feature2", "feature3", "feature4"]
Create Spark session and streaming context
spark = SparkSession.builder.appName(APP_NAME).getOrCreate()
ssc = StreamingContext(spark.sparkContext, BATCH_DURATION)
Define input stream from Kafka topic
kafka_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", INPUT_TOPIC) \
    .load()
Parse input stream data from JSON to DataFrame
input_schema = StructType([
    StructField("feature1", DoubleType()),
    StructField("feature2", DoubleType()),
    StructField("feature3", DoubleType()),
    StructField("feature4", DoubleType())
])
parsed_stream = kafka_stream \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), input_schema).alias("parsed_data")) \
    .select("parsed_data.*")
Assemble features vector
assembler = VectorAssembler(inputCols=FEATURE_COLUMNS, outputCol="features")
assembled_stream = assembler.transform(parsed_stream).select("features")
Load model
model = PipelineModel.load(MODEL_PATH)
Predict on streaming data and write output to new Kafka topic
def classify_and_write_output(batch_df, batch_id):
    predictions = model.transform(batch_df)
    output_df = predictions.select(to_json(struct(col("*"))).alias("value"))
    output_df \
        .write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("topic", OUTPUT_TOPIC) \
        .save()
Create streaming job
query = assembled_stream \
    .writeStream \
    .foreachBatch(classify_and_write_output) \
    .trigger(processingTime=str(BATCH_DURATION) + " seconds") \
    .start()
Wait for the streaming job to finish
query.awaitTermination()

structured streaming pipeline MLOPs pipeline for classification machine learning model with trigger of new data ingestion and write output to new kafka topic

Code Snippet - 

import necessary libraries
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql.functions import from_json, col, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql import SparkSession
create SparkSession
spark = SparkSession.builder.appName("MLOpsPipeline").getOrCreate()
define schema for incoming data
input_schema = StructType([
  StructField("feature1", DoubleType(), True),
  StructField("feature2", DoubleType(), True),
  StructField("feature3", DoubleType(), True),
  StructField("label", DoubleType(), True)
])
define schema for output data
output_schema = StructType([
  StructField("prediction", DoubleType(), True),
  StructField("probability", StringType(), True)
])
read incoming data from Kafka
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "localhost:9092") \
  .option("subscribe", "input_topic") \
  .option("startingOffsets", "earliest") \
  .load()
convert the incoming data to a dataframe with the defined schema
df = df.selectExpr("CAST(value AS STRING)") \
  .select(from_json(col("value"), input_schema).alias("data")) \
  .select(col("data.*"))
create feature vector assembler
assembler = VectorAssembler(
  inputCols=["feature1", "feature2", "feature3"],
  outputCol="features"
)
create logistic regression model
lr = LogisticRegression(
  featuresCol="features",
  labelCol="label",
  predictionCol="prediction",
  probabilityCol="probability",
  maxIter=10
)
create a pipeline for feature vector assembler and logistic regression model
pipeline = Pipeline(stages=[assembler, lr])
fit the pipeline to the training data
model = pipeline.fit(df)
write output to Kafka
output = model.transform(df) \
  .select(to_json(struct(col("*"))).alias("value")) \
  .writeStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "localhost:9092") \
  .option("checkpointLocation", "checkpoints") \
  .option("topic", "output_topic") \
  .trigger(processingTime='10 seconds') \
  .start()
start the stream
output.awaitTermination()

Explaination - 

Import necessary libraries - importing required packages and libraries for building the pipeline.
Create SparkSession - create a new Spark session with the name "MLOpsPipeline".
Define schema for incoming data - define the schema of the incoming data, including feature1, feature2, feature3, and label.
Define schema for output data - define the schema of the output data, including prediction and probability.
Read incoming data from Kafka - read incoming data from Kafka with the defined schema.
Convert the incoming data to a dataframe with the defined schema - convert the incoming data to a dataframe with the defined schema by using the from_json() function.
Create feature vector assembler - create a feature vector assembler to assemble feature1, feature2, and feature3 into a single feature column called "features".
Create logistic regression model - create a logistic regression model with featuresCol="features", labelCol="label", predictionCol="prediction", probabilityCol="probability", and maxIter=10.
Create a pipeline for feature vector assembler and logistic regression model - create a pipeline with the assembler and logistic regression model.
Fit the pipeline to the training data - fit the pipeline to the training data.
Write output to Kafka - write the output to Kafka with to_json() function, where we select all columns and convert them to a JSON string.
Start the stream - start the stream with awaitTermination() function.

Mlops pipeline with spark stuctured streaming which trigger on everytime new data ingested after 24 hours  and train the model and save to model to desktop directory submit and  this as spark job 

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
import time
Define the data schema
data_schema = "feature1 FLOAT, feature2 FLOAT, feature3 FLOAT, feature4 FLOAT, label INT"
Define the batch interval (in seconds) for streaming
batch_interval = 60
Define the directory to save the trained model
model_directory = "/Users/myusername/Desktop/my_model"
Create a SparkSession
spark = SparkSession.builder \
    .appName("MLOps-Spark-Streaming") \
    .getOrCreate()
Define the streaming data source
streaming_df = spark.readStream \
    .format("csv") \
    .option("header", "true") \
    .schema(data_schema) \
    .load("/path/to/streaming/data/directory")
Define the preprocessing steps
assembler = VectorAssembler(
    inputCols=["feature1", "feature2", "feature3", "feature4"],
    outputCol="features"
)

Define the training function
def train_model(df):
    if df.count() > 0:
        # Preprocess the data
        preprocessed_df = assembler.transform(df)
        # Train the model
        model = lr.fit(preprocessed_df)
        # Save the model
        model.save(model_directory)

Define the training step
lr = LogisticRegression(featuresCol="features", labelCol="label")
Define the streaming query
query = streaming_df \
    .withColumnRenamed("label", "target") \
    .withWatermark("timestamp", "24 hours") \
    .groupBy(window("timestamp", "24 hours")) \
    .agg(avg(col("feature1")).alias("feature1"),
         avg(col("feature2")).alias("feature2"),
         avg(col("feature3")).alias("feature3"),
         avg(col("feature4")).alias("feature4"),
         max(col("target")).alias("label")) \
    .withColumn("timestamp", current_timestamp()) \
    .select("timestamp", "feature1", "feature2", "feature3", "feature4", "label") \
    .writeStream \
    .trigger(processingTime="24 hours") \
    .foreachBatch(lambda df, epoch_id: train_model(df)) \
    .start()

Wait for the query to finish
query.awaitTermination()
Stop the SparkSession
spark.stop()

To submit this code as a Spark job, you can package the code into a JAR file using sbt or maven, and then submit the JAR file to a Spark cluster using the spark-submit command. Here's an example spark-submit command:

$SPARK_HOME/bin/spark-submit \
    --class com.example.mlops.MLOpsPipeline \
    --master yarn \
    --deploy-mode client \
    my-mlops-pipeline.jar



Mlops pipeline with MLFLOW which trigger on everytime new data ingested after 30 Minutes   and train the model and save to model to desktop directory submit and  this as spark job

Import required libraries
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
import mlflow
import os
import time
Define constants
MODEL_DIR = "file:///home/user/Desktop/model"
EXPERIMENT_NAME = "My Experiment"
FEATURE_COLUMNS = ["feature1", "feature2", "feature3", "feature4"]
TRIGGER_INTERVAL = 1800  # 30 minutes
Start MLflow run
with mlflow.start_run(run_name="My Run") as run:
    # Log experiment name and run ID
    experiment_id = run.info.experiment_id
    mlflow.log_param("experiment_id", experiment_id)
    mlflow.log_param("run_id", run.info.run_id)
    # Load data and split into training and validation sets
    data = spark.read.csv("data.csv", header=True, inferSchema=True)
    training_data, validation_data = data.randomSplit([0.7, 0.3], seed=42)
    # Preprocess data
    assembler = VectorAssembler(inputCols=FEATURE_COLUMNS, outputCol="features")
    training_data = assembler.transform(training_data).select("features", "label")
    validation_data = assembler.transform(validation_data).select("features", "label")
    # Train model and log metrics
    lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)
    model = lr.fit(training_data)
    train_predictions = model.transform(training_data)
    train_accuracy = train_predictions.filter(train_predictions.label == train_predictions.prediction).count() / float(training_data.count())
    mlflow.log_metric("train_accuracy", train_accuracy)
    validation_predictions = model.transform(validation_data)
    validation_accuracy = validation_predictions.filter(validation_predictions.label == validation_predictions.prediction).count() / float(validation_data.count())
    mlflow.log_metric("validation_accuracy", validation_accuracy)
    # Save model to desktop directory
    model.save(MODEL_DIR)
    # Log model artifacts
    mlflow.log_artifact(MODEL_DIR)
    # Sleep until next trigger interval
    time.sleep(TRIGGER_INTERVAL)
End MLflow run
mlflow.end_run()

To submit this code as a Spark job, you can package it as a JAR file and submit it using the spark-submit command. For example:

$ sbt package
$ spark-submit --class com.example.MyApp --master local[4] target/scala-2.12/myapp_2.12-1.0.jar

Replace com.example.MyApp with the fully qualified name of your application class, and target/scala-2.12/myapp_2.12-1.0.jar with the path to your JAR file. You may also need to adjust the --master option depending on your Spark cluster setup.