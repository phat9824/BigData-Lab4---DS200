# model.py
from pyspark.ml.regression import LinearRegression
from pyspark.sql.dataframe import DataFrame
from pyspark.ml.evaluation import RegressionEvaluator
import numpy as np

class LinearRegressionModel:
    def __init__(self, elasticNetParam=0.0, regParam=0.1):
        self.model = None
        self.elasticNetParam = elasticNetParam
        self.regParam = regParam

    def train(self, df: DataFrame):
        if df.count() == 0:
            return [], 0.0, 0.0, 0.0, 0.0

        if self.model is None:
            self.model = LinearRegression(
                featuresCol="features",
                labelCol="label",
                maxIter=100,
                elasticNetParam=self.elasticNetParam,
                regParam=self.regParam
            )
        
        model = self.model.fit(df)
        predictions = model.transform(df)
        
        # Calculate evaluation metrics
        evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction")
        rmse = evaluator.evaluate(predictions, {evaluator.metricName: "rmse"})
        mse = evaluator.evaluate(predictions, {evaluator.metricName: "mse"})
        mae = evaluator.evaluate(predictions, {evaluator.metricName: "mae"})
        r2 = evaluator.evaluate(predictions, {evaluator.metricName: "r2"})

        pred_list = predictions.select("prediction").rdd.flatMap(lambda x: x).collect()
        return pred_list, rmse, mse, mae, r2

    def predict(self, df: DataFrame, raw_model=None):
        if df.count() == 0:
            return 0.0, 0.0, 0.0, 0.0

        predictions = self.model.transform(df)
        
        # Calculate evaluation metrics
        evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction")
        rmse = evaluator.evaluate(predictions, {evaluator.metricName: "rmse"})
        mse = evaluator.evaluate(predictions, {evaluator.metricName: "mse"})
        mae = evaluator.evaluate(predictions, {evaluator.metricName: "mae"})
        r2 = evaluator.evaluate(predictions, {evaluator.metricName: "r2"})
        
        return rmse, mse, mae, r2
