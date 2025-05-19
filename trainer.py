# trainer.py
from pyspark.context import SparkContext
from pyspark.streaming.context import StreamingContext
from pyspark.sql.context import SQLContext
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import DoubleType, StructField, StructType
from pyspark.ml.linalg import VectorUDT
from transforms import Transforms
import pyspark

import numpy as np
import os
transforms_file = os.path.abspath("transforms.py")

class SparkConfig:
    appName = "StudentDataSVM"
    receivers = 4  
    host = "local"
    stream_host = "localhost"
    port = 6100
    batch_interval = 10

from dataloader import DataLoader

class Trainer:
    def __init__(self, 
                 model, 
                 split: str, 
                 spark_config: SparkConfig, 
                 transforms: Transforms):
        self.model = model
        self.split = split
        self.sparkConf = spark_config
        self.transforms = transforms
        self.sc = SparkContext(f"{self.sparkConf.host}[{self.sparkConf.receivers}]", f"{self.sparkConf.appName}")
        self.ssc = StreamingContext(self.sc, self.sparkConf.batch_interval)
        self.sqlContext = SQLContext(self.sc)
        self.dataloader = DataLoader(self.sc, self.ssc, self.sqlContext, self.sparkConf, self.transforms)
        self.total_batches = 0
        self.mse = 0.0
        self.rmse = 0.0
        self.mae = 0.0
        self.r2 = 0.0
        self.batch_count = 0
        self.sc.addPyFile(transforms_file)
    
    def train(self):
        stream = self.dataloader.parse_stream()
        stream.foreachRDD(self.__train__)
        self.ssc.start()
        self.ssc.awaitTermination()

    def __train__(self, timestamp, rdd: pyspark.RDD) -> DataFrame:
        print(f"RDD: {rdd.take(1)}")
        if not rdd.isEmpty():
            sample = rdd.take(1)[0]
            print(f"Features type: {type(sample[0])}, Features shape: {np.array(sample[0]).shape if isinstance(sample[0], (list, np.ndarray)) else 'N/A'}")

            schema = StructType([
                StructField("features", VectorUDT(), True),  # Feature vector
                StructField("label", DoubleType(), True)     # Using DoubleType for regression
            ])

            try:
                df = self.sqlContext.createDataFrame(rdd, schema)
                print(f"DataFrame created: {df.take(1)}")
                predictions, rmse, mse, mae, r2 = self.model.train(df)
                print("="*10)
                print(f"Predictions = {predictions[:5]}...")  # Show first 5 predictions
                print(f"RMSE = {rmse:.2f}")
                print(f"MSE = {mse:.2f}")
                print(f"MAE = {mae:.2f}")
                print(f"R2 Score = {r2:.2f}")
                print("="*10)
            except Exception as e:
                print(f"Error creating DataFrame or training: {e}")
        self.total_batches += rdd.count()
        print("Total Batch Size of RDD Received:", rdd.count())
        print("+"*20)

    def predict(self):
        stream = self.dataloader.parse_stream()
        stream.foreachRDD(self.__predict__)
        self.ssc.start()
        self.ssc.awaitTermination()

    def __predict__(self, rdd: pyspark.RDD) -> DataFrame:
        self.batch_count += 1
        if not rdd.isEmpty():
            schema = StructType([
                StructField("features", VectorUDT(), True),
                StructField("label", DoubleType(), True)
            ])
            try:
                df = self.sqlContext.createDataFrame(rdd, schema)
                rmse, mse, mae, r2 = self.model.predict(df, self.model)
                self.rmse += rmse / max(self.total_batches, 1)
                self.mse += mse / max(self.total_batches, 1)
                self.mae += mae / max(self.total_batches, 1)
                self.r2 += r2 / max(self.total_batches, 1)
                print(f"Test RMSE: {self.rmse:.2f}")
                print(f"Test MSE: {self.mse:.2f}")
                print(f"Test MAE: {self.mae:.2f}")
                print(f"Test R2 Score: {self.r2:.2f}")
            except Exception as e:
                print(f"Error in prediction: {e}")
        print(f"batch: {self.batch_count}")
        print("Total Batch Size of RDD Received:", rdd.count())
        print("---------------------------------------")
        exit(0)
