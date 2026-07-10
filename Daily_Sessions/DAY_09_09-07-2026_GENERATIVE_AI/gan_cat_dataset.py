import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torchvision.utils import save_image
from torch.utils.data import DataLoader

# ---------------- Config ----------------
DATASET_DIR = "Cat_Dataset"
OUTPUT_DIR = "generated_images"
MODEL_DIR = "models"

IMAGE_SIZE = 64
BATCH_SIZE = 64
LATENT_DIM = 100
CHANNELS = 3
FEATURES_G = 64
FEATURES_D = 64
EPOCHS = 50
LR = 2e-4
BETA1 = 0.5

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

transform = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.CenterCrop(IMAGE_SIZE),
    transforms.ToTensor(),
])
