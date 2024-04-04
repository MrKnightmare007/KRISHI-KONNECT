# Importing required functions
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template
import os
import joblib
import requests
from datetime import datetime,timedelta

yes,no=[],[]
presentday = datetime.now()
for i in range(0,4):
     a = presentday-timedelta(4-i)
     yes.append(a.strftime("%d"))
for i in range(0,5):
     b = presentday+timedelta(i+1)    
     no.append(b.strftime("%d"))
url = "https://api.tomorrow.io/v4/weather/forecast?location=kolkata&timesteps=daily&apikey=NWbU1ceSDImxoVp6CmKLzUrXScmgL1c2"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)
data = response.json()  # Parse the JSON response

# Extract the daily forecast data for 5 days
daily_forecast = data['timelines']['daily'][:5]

# Initialize lists to store extracted data
temperature_data = []
humidity_data = []
pressure_data = []
windspeed_data = []
rain_data = []
moisture_data = []

# Extract data for each day
for day_data in daily_forecast:
    temperature = day_data['values']['temperatureAvg']
    humidity = day_data['values']['humidityAvg']
    pressure = day_data['values']['pressureSurfaceLevelAvg']
    windspeed = day_data['values']['windSpeedAvg']
    rain = day_data['values']['rainAccumulationAvg']
    
    # Add your code here to calculate or fetch moisture data
    # For now, I'm setting it to a placeholder value
    
    
    # Append data to respective lists
    temperature_data.append(temperature)
    humidity_data.append(humidity)
    pressure_data.append(pressure)
    windspeed_data.append(windspeed)
    rain_data.append(rain)


model = joblib.load('soil_moisture_model.pkl')

# Create a list of input values and reshape it to match the model's input format
for day in range(5):
    input_data = [[temperature_data[day], humidity_data[day], pressure_data[day]/10, windspeed_data[day], rain_data[day]]]

    # Make predictions
    soil_moisture_prediction = model.predict(input_data)

    # Print the predicted soil moisture value
    moisture_data.append(round(soil_moisture_prediction[0]*100, 2))


# Flask constructor
app = Flask(__name__)

# Generate a scatter plot and returns the figure

x = np.array([yes[0],yes[1],yes[2],yes[3],presentday.strftime("%d"),no[0],no[1],no[2],no[3],no[4]]) # array to be plotted
y = np.array([60,50,55,69,63,0,0,0,0,0]) # array to be plotted
for i in range(5):
    y[5+i] = moisture_data[i]

subArray = [60,moisture_data[4]] 
ids = np.nonzero(np.in1d(y, subArray))[0]

plt.plot(x,y)
plt.plot(x[ids], y[ids], 'bo')
plot = plt

# Save the figure in the static directory
plot.savefig(os.path.join('static', 'images', 'plot.png'))
print("plot-generator")

# Root URL
@app.get('/')
def single_converter():
    # Get the matplotlib plot
    
    
    return render_template('chart.html')

# Main Driver Function
if __name__ == '__main__':
	# Run the application on the local development server
	app.run(debug=True)