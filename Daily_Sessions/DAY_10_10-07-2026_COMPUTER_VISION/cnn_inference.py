from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt

img_path = "/test1.jpg"

# Note: 'model' and 'class_names' should be defined before running this
img = image.load_img(img_path, target_size=(128, 128))
img_array = image.img_to_array(img)

img_array = img_array / 255.0

img_array = np.expand_dims(img_array, axis=0)

predictions = model.predict(img_array)
predicted_class_index = np.argmax(predictions[0])
predicted_class_name = class_names[predicted_class_index]
confidence = np.max(predictions[0])

plt.imshow(img)
plt.title(f"Prediction: {predicted_class_name} ({confidence:.2f})")
plt.axis('off')
plt.show()

print("Predicted class:", predicted_class_name)
print("Confidence:", confidence)
