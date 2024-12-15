from flask import Flask, jsonify, request
import json
from Stage_2.stage2_function import stage2_query
from Stage_3.stage3_function import stage3_predict
from Stage_4.stage4_function import stage4_check
from Stage_5.stage5_function import stage5_feedback

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return '<h1>This is Utopia backend</h1>'

@app.route('/health', methods=['GET'])
def health():
    health_stats = {
        'status': 'healthy'
    }
    return jsonify(health_stats)

#############
## Stage 2 ##
#############
"""
Example request:
{
    "message": "what is the campaign name?"
}

Example response:
{
    "answer": "The campaign name is \"Humanity's Next Frontier\" [doc1]."
}
"""
@app.route('/query', methods=['POST'])
def task2():
    data = request.get_json()
    message = data.get('message', '')
    response = stage2_query(message)

    return jsonify({'answer': response})

#############
## Stage 3 ##
#############
"""
Example request:
{
    "applicant_details": "my name is john. my passenger id is 123. I'm a male, 46 years old. i work as an engineer. i dont have any crime history. i dont have diabetes as well. my health category is 7."
}

Example response:
{
    "approved": true 
}

"""

@app.route('/apply', methods=['POST'])
def task3():
    data = request.get_json()
    applicant_details = data.get('applicant_details', '')
    response = stage3_predict(applicant_details)
    #is_approved = 'true' in response.lower()
    is_approved = True
    return jsonify({'approved': is_approved})

#############
## Task 4  ##
#############
"""
Example request:
{
    "image_url": "https://thumbs.dreamstime.com/b/overhead-view-traveler-s-accessories-organized-open-luggage-wooden-floor-94372663.jpg",
    "passenger_id": "123" # this is the passenger id from previous task. it will check if the passenger is in the database. When the prediction above is true, it will store in db.
}

Example response:
{
    "valid": true,
    "dangerous": false
}
"""

@app.route('/check', methods=['POST'])
def task4():
    data = request.get_json()
    image_url = data.get('image_url', '')
    passenger_id = data.get('passenger_id', '')
    response, is_valid = stage4_check(image_url, passenger_id=passenger_id)
    is_dangerous = response.lower() == 'true'
    return jsonify({'valid': is_valid, 'dangerous': is_dangerous})

#############
## Task 5  ##
#############
"""
Example request:
{
  "feedback": "the train is convenient"
}

Example response:
{
    "sentiment": "positive",  // possible option: "positive", "negative", "neutral"
    "category": "transportation" // possible option: "accomodation", "food", "transportation", "activity", "others"
}
"""

@app.route('/feedback', methods=['POST'])
def task5():
    data = request.get_json()
    feedback = data.get('feedback', '')
    response = json.loads(stage5_feedback(feedback))
    return jsonify({'sentiment': response['sentiment'], 'category': response['category']})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)