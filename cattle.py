import pandas as pd
import joblib
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Load the test dataset
test_data = pd.read_csv("Testing.csv")

# Load the Decision Tree model
decision_tree_model = joblib.load('decision_tree_model.pkl')

# Extract features (X) and target variable (y) from the test dataset
X_test = test_data[['symptom1', 'symptom2', 'symptom3', 'symptom4', 'symptom5']]
y_test = test_data['prognosis']

# Make predictions on the test set
y_pred = decision_tree_model.predict(X_test)

# Print predictions
print("Predictions:")
print(y_pred)

# Print accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")
