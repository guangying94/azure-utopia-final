import joblib
import pandas as pd

# Function for inferencing
def infer(input_data):
    # Load the model and label encoders
    model = joblib.load('model.pkl')
    label_encoders = joblib.load('label_encoders.pkl')
    
    # Preprocess the input data
    for column in ['sex', 'occupation', 'crime_history', 'diabetes']:
        le = label_encoders[column]
        input_data[column] = le.transform([input_data[column]])[0]
    
    # Convert input data to DataFrame
    input_df = pd.DataFrame([input_data])
    
    # Predict
    prediction = model.predict(input_df)
    
    return prediction[0]

# Example usage
#input_data = {
#    'age': 30,
#    'sex': 'male',
#    'occupation': 'engineer',
#    'crime_history': 'False',
#    'health': 7,
#    'diabetes': 'True'
#}
#print(infer(input_data))