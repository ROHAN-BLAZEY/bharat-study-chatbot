import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import numpy as np
import os

base_data_dir = "/content/dataset/flowers"
data_dir = base_data_dir

# Check if the directory actually exists
if not os.path.isdir(data_dir):
    found_data_dir = None
    for root, dirs, files in os.walk(base_data_dir):
        if dirs:
            for subdir in dirs:
                sub_path = os.path.join(root, subdir)
                if os.path.isdir(sub_path):
                    # Check if any image files are present in subdirectories to confirm it's a dataset root
                    for _, _, subfiles in os.walk(sub_path):
                        if any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in subfiles):
                            found_data_dir = sub_path
                            break
