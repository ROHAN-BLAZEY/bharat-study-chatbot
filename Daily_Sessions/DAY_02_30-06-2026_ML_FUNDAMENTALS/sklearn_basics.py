from sklearn.linear_model import LinearRegression
import numpy as np

# Sample data
X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])

# Initialize and train model
model = LinearRegression()
model.fit(X, y)

# Predict
test_data = np.array([[6], [7]])
predictions = model.predict(test_data)

print(f"Predictions for {test_data.flatten()}: {predictions}")
