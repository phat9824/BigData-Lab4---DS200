import time
import json
import socket
import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Streams Student Data to Spark Streaming Context')
parser.add_argument('--batch-size', '-b', help='Batch size', required=True, type=int)
parser.add_argument('--endless', '-e', help='Enable endless stream', type=bool, default=False)
parser.add_argument('--split', '-s', help="training or test split", type=str, default='train')
parser.add_argument('--sleep', '-t', help="streaming interval", type=int, default=3)

TCP_IP = "localhost"
TCP_PORT = 6100

class Dataset:
    def __init__(self):
        self.data = []
        self.labels = []
        df = pd.read_csv("datasets/Student_Data.csv")
        # Extract numeric features only
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
        
        # Drop student_id and target variable (exam_score)
        self.data = df_encoded.drop(columns=['student_id', 'exam_score']).values
        self.labels = df['exam_score'].values.tolist()

    def data_generator(self, batch_size):
        batch = []
        size_per_batch = (len(self.data) // batch_size) * batch_size
        for ix in range(0, size_per_batch, batch_size):
            features = self.data[ix:ix+batch_size]
            labels = self.labels[ix:ix+batch_size]
            batch.append([features, labels])
        return batch

    def sendStudentDataToSpark(self, tcp_connection, batch_size, split="train"):
        total_samples = len(self.data)  # Total samples in the dataset
        total_batch = total_samples // batch_size + (1 if total_samples % batch_size else 0)
        pbar = tqdm(total=total_batch)
        data_received = 0

        batches = self.data_generator(batch_size)
        for batch in batches:
            features, labels = batch
            features = np.array(features)
            batch_size, feature_size = features.shape
            features = features.tolist()

            payload = dict()
            for batch_idx in range(batch_size):
                payload[batch_idx] = dict()
                for feature_idx in range(feature_size):
                    payload[batch_idx][f'feature-{feature_idx}'] = features[batch_idx][feature_idx]
                payload[batch_idx]['label'] = labels[batch_idx]

            payload = (json.dumps(payload) + "\n").encode()
            try:
                tcp_connection.send(payload)
            except (BrokenPipeError, ConnectionResetError) as e:
                print(f"Connection error: {e}. Reconnecting...")
                tcp_connection.close()
                tcp_connection, _ = self.connectTCP()
                tcp_connection.send(payload)
            except Exception as error_message:
                print(f"Exception thrown but was handled: {error_message}")

            data_received += 1
            pbar.update(n=1)
            pbar.set_description(f"it: {data_received} | received: {batch_size} samples")
            time.sleep(sleep_time)
        return tcp_connection

    def connectTCP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        print(f"Waiting for connection on port {TCP_PORT}...")
        connection, address = s.accept()
        print(f"Connected to {address}")
        return connection, address

    def streamStudentDataset(self, tcp_connection, batch_size, train_test_split):
        tcp_connection = self.sendStudentDataToSpark(tcp_connection, batch_size, train_test_split)
        return tcp_connection

if __name__ == '__main__':
    args = parser.parse_args()
    batch_size = args.batch_size
    endless = args.endless
    sleep_time = args.sleep
    train_test_split = args.split
    dataset = Dataset()
    tcp_connection, _ = dataset.connectTCP()

    if endless:
        while True:
            tcp_connection = dataset.streamStudentDataset(tcp_connection, batch_size, train_test_split)
    else:
        tcp_connection = dataset.streamStudentDataset(tcp_connection, batch_size, train_test_split)
    print('Stop here')
    tcp_connection.close()