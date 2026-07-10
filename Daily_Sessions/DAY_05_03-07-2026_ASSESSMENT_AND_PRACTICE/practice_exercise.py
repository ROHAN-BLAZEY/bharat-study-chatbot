# Practice Exercise: Data Normalization
import numpy as np

def normalize_data(data):
    """Normalizes data to have mean 0 and standard deviation 1."""
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    normalized = (data - mean) / (std + 1e-8) # Add small epsilon to prevent division by zero
    return normalized

data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
print("Original Data:\n", data)
print("Normalized Data:\n", normalize_data(data))
