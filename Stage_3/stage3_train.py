import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load the dataset
data = pd.read_csv('data.csv')

# Preprocess the data
# Encode categorical variables
label_encoders = {}
for column in ['sex', 'occupation', 'crime_history', 'diabetes']:
    le = LabelEncoder()
    data[column] = le.fit_transform(data[column])
    label_encoders[column] = le

# Split the data into features and target
X = data.drop(columns=['accepted', 'id'])
y = data['accepted']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple classification model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save the model and label encoders
joblib.dump(model, 'model.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')