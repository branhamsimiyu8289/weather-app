# Weather App CLI

A command-line application that queries OpenStreetMap's Nominatim API for
settlement geocoding and fetches live, localized weather data via the OpenWeather
API.

## ✨ Features

- **Settlement Geocoding:** Filters out administrative regions, countries, and
  non-settlement locations using OpenStreetMap Nominatim data.
- **Live Weather Metrics:** Displays temperature, humidity, wind speed, and
  atmospheric conditions.
- **Local Time & Astronomical Tracking:** Displays local sunrise and sunset
  times based on the location's time offset.
- **Error & Rate-Limit Handling:** Spaces batch geocoding requests and handles
  network failures and invalid locations.

## 🛠️ Technology Used

- **Python 3.x**
- **Requests** for HTTP requests
- **Python-dotenv** for environment variable management
- **OpenStreetMap Nominatim API** for geocoding
- **OpenWeatherMap API** for weather data

## 📂 Project Structure

```text
day-2/
├── .env                 # Local API key; ignored by Git
├── .env.example         # Environment variable template
├── .gitignore
├── day2_weatherapi.py   # Application source code
├── README.md
└── requirements.txt
```

## 🔄 System Flow

1. **Initialization:** Loads `OPENWEATHER_API_KEY` from `.env` using
   `python-dotenv`.
2. **User Input:** Prompts for a comma-separated list of city or settlement
   names.
3. **Geocoding Validation:** Queries Nominatim and validates that each result
   is a settlement.
4. **Weather Fetch:** Sends the validated coordinates to OpenWeatherMap.
5. **Formatting & Output:** Displays weather conditions, temperatures, wind,
   humidity, sunrise, and sunset.

## 🏗️ Architecture

The application separates string normalization, place validation, network
requests, and presentation:

- **Normalization & Validation:** Sanitizes Unicode strings with
  `normalize_name`, tokenizes search inputs, and checks settlement types.
- **Geocoding (`lookup_place`):** Queries Nominatim with request headers and a
  timeout.
- **Weather (`show_weather`):** Queries OpenWeatherMap and formats the returned
  weather and local time data.

## 🚀 Example Output

```text
    ============WEATHER APP============
       Welcome to my weather app
Enter city names separated by commas: Nairobi, London

        ----------- Nairobi ------------
   Weather: ⛅ Scattered Clouds
   Temperature: 🌡️ 24.5°C
   Humidity: 💧 58% | Wind speed: 🌬️ 12.6 km/h
   Sunrise: 🌅 06:21 AM | Sunset: 🌇 06:33 PM
      -----------------------------------
```

Weather values vary with the location and time of the request.

## 🧠 Learning Focus

- **API Integration:** Consuming REST APIs with request timeouts and appropriate
  headers.
- **Data Sanitization & Parsing:** Processing JSON responses and normalizing
  multilingual location queries with Python's `unicodedata` and `re` modules.
- **Defensive Programming:** Handling network failures and invalid responses.

## ⚙️ Setup and Usage

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenWeatherMap API key:

```dotenv
OPENWEATHER_API_KEY=your_real_api_key
```

The `.env` file is ignored by Git. Do not commit or share your API key.

Run the app from this directory:

```powershell
python day2_weatherapi.py
```

## 👤 Author

- **Branham Simiyu**
