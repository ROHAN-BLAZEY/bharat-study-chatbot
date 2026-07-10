from google.colab import files
import zipfile
import os

zip_path = "/content/dataset.zip"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall('/content/dataset')

os.remove(zip_path)

print("File extracted and removed successfully.")
