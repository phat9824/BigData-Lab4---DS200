import numpy as np

class Transforms:
    def __init__(self, transforms_list):
        self.transforms_list = transforms_list
    
    def transform(self, features):
        for transform in self.transforms_list:
            features = transform(features)
        return features

class Normalize:
    def __init__(self, mean, std):
        self.mean = np.array(mean)
        self.std = np.array(std)
    
    def __call__(self, features):
        features = np.array(features)
        return ((features - self.mean) / (self.std + 1e-8)).tolist()