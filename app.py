from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

WEATHER_API_KEY = 'be19023d2adb4aeb8e245401240811'
GEODB_API_KEY = '41fd5c2711msh409924e8e12130bp1e7938jsncea05d95606e'

# Fetch weather data from the WeatherAPI
def get_weather_data(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&alerts=yes"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Fetch city suggestions from GeoDB Cities API
def get_city_suggestions(query):
    url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
    headers = {
        "X-RapidAPI-Key": GEODB_API_KEY,
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }
    params = {
        "namePrefix": query,
        "limit": 5,
        "types": "CITY"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# Farming suggestions based on weather conditions
def get_farming_suggestions(weather_condition, temp_c):
    suggestions = []

    # Based on weather condition
    if 'rain' in weather_condition.lower():
        suggestions.append("Ensure proper drainage to avoid waterlogging and root rot.")
        suggestions.append("Check for potential crop diseases caused by excessive moisture.")
    elif 'sun' in weather_condition.lower() or 'clear' in weather_condition.lower():
        suggestions.append("Irrigate your crops to prevent dehydration.")
        suggestions.append("Provide shade for heat-sensitive crops during the hottest parts of the day.")
    elif 'cloud' in weather_condition.lower():
        suggestions.append("Keep an eye on weather patterns as cloudy days could bring unexpected rains.")
        suggestions.append("Ensure crops are getting enough sunlight despite overcast conditions.")
    elif 'snow' in weather_condition.lower() or 'cold' in weather_condition.lower():
        suggestions.append("Protect your crops from frost by using row covers or other insulating materials.")
        suggestions.append("Monitor soil moisture, as cold weather may prevent evaporation.")
    elif 'hot' in weather_condition.lower() or temp_c > 30:
        suggestions.append("Water crops early in the morning to reduce heat stress.")
        suggestions.append("Consider mulching to keep the soil cool and retain moisture.")

    # Based on temperature
    if temp_c > 30:
        suggestions.append("Ensure frequent watering to avoid crops from drying out.")
    elif temp_c < 10:
        suggestions.append("Use frost protection methods for sensitive crops.")
    
    return suggestions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form.get('city')
    weather_data = get_weather_data(city)
    
    if not weather_data:
        return jsonify({"error": "City not found or API issue."})
    
    # Extract weather and alert information
    current_weather = {
        "location": weather_data['location']['name'],
        "temp_c": weather_data['current']['temp_c'],
        "condition": weather_data['current']['condition']['text'],
        "icon": weather_data['current']['condition']['icon']
    }
    
    alerts = weather_data.get('alerts', {}).get('alert', [])
    
    suggestions = get_farming_suggestions(current_weather['condition'], current_weather['temp_c'])
    
    return jsonify({
        "weather": current_weather,
        "alerts": alerts,
        "suggestions": suggestions
    })

@app.route('/get_cities')
def get_cities():
    query = request.args.get('query')
    cities = get_city_suggestions(query)
    return jsonify(cities)

if __name__ == '__main__':
    app.run(debug=True)
