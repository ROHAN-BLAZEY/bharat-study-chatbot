from inference_sdk import InferenceHTTPClient
from google.colab.patches import cv2_imshow
import cv2

# ---------------------------------
# Roboflow Configuration
# ---------------------------------
API_KEY = "YOUR_NEW_ROBOFLOW_API_KEY"

MODEL_ID = "vinayaks-workspace-pu/vin-r1isy-instant-1"

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=API_KEY
)

# ---------------------------------
# Image Path
# ---------------------------------
image_path = "/content/images (5).jpg"

# ---------------------------------
# Run Inference
# ---------------------------------
result = CLIENT.infer(
    image_path,
    model_id=MODEL_ID
)

print(result)
