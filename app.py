from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# OpenWeatherMap API settings
API_KEY = '74783f89a0888bb58223a6054a0bde52'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            error_message = 'Please enter a city name'
            return render_template('index.html', error_message=error_message)

        url = f'{BASE_URL}?q={city}&appid={API_KEY}&units=metric'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            error_message = handle_http_error(http_error)
            return render_template('index.html', error_message=error_message)
        except requests.exceptions.ConnectionError:
            error_message = 'Connection Error: Please check your internet connection'
            return render_template('index.html', error_message=error_message)
        except requests.exceptions.Timeout:
            error_message = 'Timeout Error: The request timed out'
            return render_template('index.html', error_message=error_message)
        except requests.exceptions.RequestException as req_error:
            error_message = f'Request Error: {req_error}'
            return render_template('index.html', error_message=error_message)

        data = response.json()
        if data['cod'] == 200:
            try:
                temperature_c = data['main']['temp']
                weather_description = data['weather'][0]['description']
                weather_id = data['weather'][0]['id']
                weather_data = {
                    'city': city,
                    'temperature': f'{temperature_c:.0f}°C',
                    'emoji': get_weather_emoji(weather_id),
                    'description': weather_description
                }
                return render_template('index.html', weather_data=weather_data)
            except KeyError as key_error:
                error_message = f'Error: Missing key {key_error}'
                return render_template('index.html', error_message=error_message)
        else:
            error_message = 'City not found'
            return render_template('index.html', error_message=error_message)
    return render_template('index.html')

def handle_http_error(http_error):
    status_code = http_error.response.status_code
    if status_code == 400:
        return 'Bad Request: Please check your input'
    elif status_code == 401:
        return 'Unauthorized: Please check your API key'
    elif status_code == 403:
        return 'Forbidden: Please check your API key'
    elif status_code == 404:
        return 'Not Found: City not found'
    elif status_code == 500:
        return 'Internal Server Error: Please try again later'
    elif status_code == 502:
        return 'Bad Gateway: Please try again later'
    elif status_code == 503:
        return 'Service Unavailable: Please try again later'
    elif status_code == 504:
        return 'Gateway Timeout: Please try again later'
    else:
        return f'HTTP Error: {status_code}'

def get_weather_emoji(weather_id):
    if weather_id >= 200 and weather_id <= 232:
        return "⛈️"
    elif 300 <= weather_id <= 321:
        return "🌦️"
    elif 500 <= weather_id <= 531:
        return "🌧️"
    elif 600 <= weather_id <= 622:
        return "❄️"
    elif 701 <= weather_id <= 741:
        return "🌫️"
    elif weather_id == 762:
        return "🌋"
    elif weather_id == 771:
        return "🍃"
    elif weather_id == 781:
        return "🌪️"
    elif weather_id == 800:
        return "☀️"
    elif 801 <= weather_id <= 804:
        return "☁️"
    else:
        return ""

if __name__ == '__main__':
    app.run(debug=True)