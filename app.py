import json
from os import environ as env
import pandas as pd
from chat import get_response
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
import requests
from datetime import datetime, timedelta
import os
import joblib
import tensorflow as tf
import base64
from io import BytesIO
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use('Agg')  # Use Agg backend
import matplotlib.pyplot as plt
from keras.preprocessing import image
from keras.models import load_model
import google.generativeai as genai

# Import statements for ML models
from potato_model.potato import predict_potato
from tomato_model.tomato import predict_tomato

# Load the trained model
model = joblib.load('trained_model.pkl')

# List of symptoms
symptoms = [
    'anorexia', 'abdominal_pain', 'anaemia', 'abortions', 'acetone', 'aggression', 'arthrogyposis', 'ankylosis', 'anxiety', 'bellowing',
    'blood_loss', 'blood_poisoning', 'blisters', 'colic', 'Condemnation_of_livers', 'coughing', 'depression', 'discomfort', 'dyspnea',
    'dysentery', 'diarrhoea', 'dehydration', 'drooling', 'dull', 'decreased_fertility', 'diffculty_breath', 'emaciation', 'encephalitis',
    'fever', 'facial_paralysis', 'frothing_of_mouth', 'frothing', 'gaseous_stomach', 'highly_diarrhoea', 'high_pulse_rate', 'high_temp',
    'high_proportion', 'hyperaemia', 'hydrocephalus', 'isolation_from_herd', 'infertility', 'intermittent_fever', 'jaundice', 'ketosis',
    'loss_of_appetite', 'lameness', 'lack_of-coordination', 'lethargy', 'lacrimation', 'milk_flakes', 'milk_watery', 'milk_clots',
    'mild_diarrhoea', 'moaning', 'mucosal_lesions', 'milk_fever', 'nausea', 'nasel_discharges', 'oedema', 'pain', 'painful_tongue',
    'pneumonia', 'photo_sensitization', 'quivering_lips', 'reduction_milk_vields', 'rapid_breathing', 'rumenstasis', 'reduced_rumination',
    'reduced_fertility', 'reduced_fat', 'reduces_feed_intake', 'raised_breathing', 'stomach_pain', 'salivation', 'stillbirths',
    'shallow_breathing', 'swollen_pharyngeal', 'swelling', 'saliva', 'swollen_tongue', 'tachycardia', 'torticollis', 'udder_swelling',
    'udder_heat', 'udder_hardeness', 'udder_redness', 'udder_pain', 'unwillingness_to_move', 'ulcers', 'vomiting', 'weight_loss', 'weakness'
]

def get_future_dates(start_date, num_days):
    dates = []
    for day in range(num_days):
        date = start_date + timedelta(days=day)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates

# Get future dates
current_date = datetime.now()
future_dates = get_future_dates(current_date, 5)
past_dates = get_future_dates(current_date - timedelta(days=5), 5)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Controllers API
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/index")

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

esp_url = "http://192.168.63.93"
# Function to fetch temperature data
def fetch_temperature():
    try:
        response = requests.get(f'{esp_url}/temperature')
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
    return "N/A"  # Return a default value if data cannot be fetched

def fetch_humidity():
    try:
        response = requests.get(f'{esp_url}/humidity')
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
    return "N/A"  # Return a default value if data cannot be fetched

def fetch_ldr():
    try:
        response = requests.get(f'{esp_url}/ldr')
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
    return "N/A"  # Return a default value if data cannot be fetched

def fetch_soil():
    try:
        response = requests.get(f'{esp_url}/soil-mois')
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
    return "N/A"  # Return a default value if data cannot be fetched

def fetch_rain():
    try:
        response = requests.get(f'{esp_url}/rain')
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
    return "N/A"  # Return a default value if data cannot be fetched


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/ldr')
def ldr():
    ldr= fetch_ldr()
    return ldr

@app.route('/temp')
def temp():
    temp = fetch_temperature()
    return temp

@app.route('/humidity')
def hum():
    hum = fetch_humidity()
    return hum

@app.route('/soil')
def soil():
    soil = fetch_soil()
    return soil

@app.route('/rain')
def rain():
    rain = fetch_rain()
    return rain

@app.route('/index1')
def index1():
    # Pass an initial value for selectedCity
    return render_template('index1.html', selectedCity="kolkata")

@app.route('/index4')
def index4():
    return render_template('index4.html')

os.environ['GOOGLE_API_KEY'] = "AIzaSyDvIm1BXLGilc89Knx0VWTfRhB5pFxgRYY"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


@app.route('/index5')
def index5():
    return render_template('index5.html')

@app.route('/index7')
def index7():
    # Initialize a list to track the disabled state of symptoms
    symptom_states = [False] * len(symptoms)

    return render_template('index7.html', symptoms=symptoms, symptom_states=symptom_states)

def get_cures(prediction):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"I want cures for a plant disease that causes {prediction}, give only 5 points in one line and don't give an asterisk at the beginning")
    cures = response.text.split('\n')[:5]
    return cures

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        # Save the uploaded file
        file_path = os.path.join('static/uploads', file.filename)
        file.save(file_path)

        # Predict based on the selected crop
        crop = request.form.get('crop')

        if crop == 'potato':
            prediction = predict_potato(file_path)  # Replace with actual prediction function
        elif crop == 'tomato':
            prediction = predict_tomato(file_path)  # Replace with actual prediction function
        else:
            prediction = "Invalid crop selection"

        # Get cures for the predicted disease
        cures = get_cures(prediction)

        # Check if the predicted disease contains the word "healthy"
        if "healthy" in prediction.lower():
            # If it's a healthy prediction, display a message accordingly
            return render_template('index5.html', prediction=prediction, cures=None)

        # Pass the prediction result and cures to the template
        return render_template('index5.html', prediction=prediction, cures=cures)

@app.route('/update_rain_plot/<city>')
def update_rain_plot(city):
    api_url = f"https://api.tomorrow.io/v4/weather/forecast?location={city}&timesteps=daily&apikey=r5MwZVAq0IiO4CH2XghAEbGPMr9lRh0f"
    
    try:
        response = requests.get(api_url, headers={"accept": "application/json"})
        data = response.json()

        daily_forecast = data['timelines']['daily'][:5]
        rain_data = [day_data['values']['rainAccumulationAvg'] for day_data in daily_forecast]

        plt.plot(future_dates, rain_data, label='Next 5 Days', color='blue', marker='o')
        plt.xticks(rotation=45)
        plt.xlabel('Date')
        plt.ylabel('Rain Accumulation (Avg)')
        plt.title(f'Predicted Rain Data for {city.capitalize()}')
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(os.path.join('static', 'images', f'rain_plot_{city}.png'))
        plt.close('all')

        return jsonify({'success': True, 'message': 'Rain plot updated successfully'})
    
    except Exception as e:
        print(f"Error updating rain plot: {e}")
        return jsonify({'success': False, 'message': 'Error updating rain plot'})

def get_future_dates(start_date, num_days):
    dates = []
    for day in range(num_days):
        date = start_date + timedelta(days=day)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates

def get_weather_data(api_key, city_name, num_days, forecast_type):
    base_url = f"https://api.tomorrow.io/v4/weather/forecast?location={city_name}&timesteps=daily&apikey={api_key}"
    headers = {"accept": "application/json"}
    response = requests.get(base_url, headers=headers)
    data = response.json()
    
    if response.status_code == 200:
        daily_forecast = data['timelines']['daily']

        if forecast_type == 'next':
            forecast_data = daily_forecast[:num_days]
        elif forecast_type == 'previous':
            forecast_data = daily_forecast[-num_days:]
        else:
            print(f"Invalid forecast_type: {forecast_type}. Use 'next' or 'previous'.")
            return None, None, None

        temperature_data = []
        humidity_data = []
        rain_data = []

        for day_data in forecast_data:
            temperature = day_data['values']['temperatureAvg']
            humidity = day_data['values']['humidityAvg']
            rain = day_data['values']['rainAccumulationAvg']

            temperature_data.append(temperature)
            humidity_data.append(humidity)
            rain_data.append(rain)

        return temperature_data, humidity_data, rain_data
    else:
        print(f"Error fetching weather data for {city_name}. Status code: {response.status_code}")
        return None, None, None

def predict_and_plot(city_name, api_key):
    global future_dates  # Use the global variable
    global current_date
    global past_dates
    # Load the soil moisture prediction model
    city_name_upper = city_name.upper()
    model = joblib.load(f"{city_name_upper}.pkl")

    # Fetch historical weather data for the previous 5 days
    previous_days_temperature, previous_days_humidity, previous_days_rain = get_weather_data(api_key, city_name, 5, 'previous')

    # Fetch forecasted weather data for the next 5 days
    future_days_temperature, future_days_humidity, future_days_rain = get_weather_data(api_key, city_name, 5, 'next')

    # Create a list of input values for previous and next days
    input_data = []
    for day in range(5):
        input_data.append([
            previous_days_temperature[day], previous_days_humidity[day], previous_days_rain[day]
        ])

    # Make predictions for the next 5 days
    soil_moisture_predictions1 = model.predict(input_data)
    
    input_data = []
    for day in range(5):
        input_data.append([
            future_days_temperature[day], future_days_humidity[day], future_days_rain[day]
        ])

    # Make predictions for the next 5 days
    soil_moisture_predictions2 = model.predict(input_data)

    # Plot soil moisture data with different colors and labels
    plt.plot(past_dates, soil_moisture_predictions1[:5], label='Previous 5 Days (Predicted)', color='blue', marker='o')

    if len(soil_moisture_predictions1) > 0:
        plt.plot(future_dates, soil_moisture_predictions2[:5], label='Next 5 Days (Predicted)', color='green', marker='o')

    # Rotate x-axis labels for better visibility
    plt.xticks(rotation=45)

    # Add labels and legend
    plt.ylim(0,1.2)
    plt.xlabel('Date')
    plt.ylabel('Soil Moisture Prediction')
    plt.legend(loc='upper left')
    plt.title(f'Soil Moisture Data for {city_name_upper}')
    plt.grid(True)

    # Save the figure
    plot_filename = f'static/images/plot_{city_name_upper}.png'
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close('all')
    return plot_filename

@app.route('/chart_soilms')
def chart():
    return render_template('chart.html')

@app.route('/update_soil_moisture_plot/<city>')
def update_soil_moisture_plot(city):
    try:
        plot_filename = predict_and_plot(city, 'r5MwZVAq0IiO4CH2XghAEbGPMr9lRh0f')
        with open(plot_filename, 'rb') as image_file:
            encoded_plot = base64.b64encode(image_file.read()).decode('utf-8')

        return jsonify({'success': True, 'message': 'Soil moisture plot updated successfully', 'plot_data': encoded_plot})
    except Exception as e:
        print(f"Error updating soil moisture plot: {e}")
        return jsonify({'success': False, 'message': 'Error updating soil moisture plot'})
    
# Route for the merged prediction page
@app.route('/predict', methods=['POST'])
def predict():
    # List of selected symptoms
    selected_symptoms = [
        request.form.get(f'symptom{i}') for i in range(1, 7)
    ]

    # Check if any symptom is not selected
    if all(symptom == '' for symptom in selected_symptoms):
        return render_template('index.html', symptoms=symptoms, predictionResult="Choose at least one Symptom")

    # Correcting feature name mismatches
    mapping = {
        'difficulty_breathing': 'diffculty_breath',
        'nasal_discharges': 'nasel_discharges',
        'reduction_milk_yields': 'reduction_milk_vields',
        'udder_hardness': 'udder_hardeness'
    }

    selected_symptoms = [mapping.get(symptom, symptom) for symptom in selected_symptoms]

    # Ensure the selected symptoms are in the same order as the 'symptoms' list
    selected_symptoms = [symptom for symptom in symptoms if symptom in selected_symptoms]

    # Create a DataFrame with user input
    user_input_df = pd.DataFrame(columns=symptoms)

    # Fill the unselected symptoms with default values (0)
    user_input_df.loc[0, selected_symptoms] = 1
    user_input_df.fillna(0, inplace=True)

    # Use the model to predict the disease
    user_pred = model.predict(user_input_df)

    # Return the predicted disease
    prediction_result = user_pred[0]

    return render_template('index7.html', symptoms=symptoms, selected_symptoms=selected_symptoms, predictionResult=prediction_result)


# Chat Application
from flask import render_template

@app.route('/chat', methods=['POST'])
def chat():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 5000))
