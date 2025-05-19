# main.py
from trainer import SparkConfig, Trainer
from model import LinearRegressionModel
from transforms import Transforms, Normalize
import pandas as pd
import numpy as np

def calculate_feature_stats():
    # This function would normally calculate statistics from your dataset
    # For this example, I'll use some default values
    try:
        df = pd.read_csv("datasets/Student_Data.csv")
        # Extract numeric features
        numeric_features = ['age', 'study_hours_per_day', 'social_media_hours', 'netflix_hours', 
                            'attendance_percentage', 'sleep_hours', 'exercise_frequency', 
                            'mental_health_rating', 'previous_gpa', 'semester', 'stress_level', 
                            'social_activity', 'screen_time', 'parental_support_level', 
                            'motivation_level', 'exam_anxiety_score', 'time_management_score']
        
        # One-hot encode categorical features
        df_encoded = pd.get_dummies(df, columns=['gender', 'major', 'diet_quality', 
                                                'parental_education_level', 'internet_quality', 
                                                'study_environment', 'learning_style', 
                                                'part_time_job', 'extracurricular_participation', 
                                                'dropout_risk', 'access_to_tutoring', 
                                                'family_income_range'])
        
        # Drop student_id and target variable
        features_df = df_encoded.drop(columns=['student_id', 'exam_score'])
        
        # Calculate means and stds
        means = features_df.mean().values
        stds = features_df.std().values
        # Replace zero stds with 1 to avoid division by zero
        stds = np.where(stds < 1e-8, 1.0, stds)
        
        return means.tolist(), stds.tolist()
    except:
        # If we can't load the dataset, use default values
        # We're using a placeholder value since we don't know the exact feature count
        # This will be dynamically determined in the DataLoader
        return [0.0] * 50, [1.0] * 50

if __name__ == "__main__":
    # Calculate feature statistics
    means, stds = calculate_feature_stats()
    
    # Define transforms
    transforms = Transforms([
        Normalize(
            mean=means,
            std=stds
        )
    ])

    # Configure Spark
    spark_config = SparkConfig()
    spark_config.receivers = 4
    spark_config.batch_interval = 10

    # Initialize model and trainer
    lr_model = LinearRegressionModel(elasticNetParam=0.1, regParam=0.1)
    trainer = Trainer(lr_model, "train", spark_config, transforms)
    
    # Train and predict
    trainer.train()
    trainer.predict()
    exit(0)
