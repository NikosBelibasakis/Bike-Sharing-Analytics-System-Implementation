import requests
import os
import json
import schedule
import time
from datetime import datetime  

# OpenWeatherMap API Key
API_KEY = "..."

# Coordinates for New York City
LATITUDE = 40.7128
LONGITUDE = -74.0060

# OpenWeatherMap API URL
WEATHER_API_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}&units=metric"

# URLs of the CitiBike API
STATION_INFO_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"

# Function to fetch weather data
def fetch_weather_data():
    try:
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status()
        data = response.json()

        # Extract required fields
        weather_data = {
            "temperature": data["main"].get("temp"),
            "precipitation": data.get("rain", {}).get("1h", 0),  # If no rain, return 0
            "wind_speed": data["wind"].get("speed"),
            "cloudiness": data["clouds"].get("all")
        }

        return weather_data

    except requests.exceptions.RequestException as err:
        print(f"Error fetching weather data: {err}")
        return None



# Function to fetch bike station information
def fetch_bike_station_information():
    try:
        response = requests.get(STATION_INFO_URL)
        response.raise_for_status()
        data = response.json()

        # Extract required fields
        stations = data["data"]["stations"]
        stations_data = [
            {
                "station_id": station["station_id"],
                "name": station["name"]
            }
            for station in stations
        ]

        return stations_data

    except requests.exceptions.RequestException as err:
        print(f"Error fetching bike station information: {err}")
        return None


# Function to fetch bike station status
def fetch_bike_station_status():
    try:
        response = requests.get(STATION_STATUS_URL)
        response.raise_for_status()
        data = response.json()

        # Extract required fields
        stations = data["data"]["stations"]

        stations_data = [
            {
                "station_id": station["station_id"],
                "num_ebikes_available": station.get("num_ebikes_available", 0),
                "num_scooters_available": station.get("num_scooters_available", 0),
                "num_scooters_unavailable": station.get("num_scooters_unavailable", 0),
                "num_docks_available": station.get("num_docks_available", 0),
                "num_docks_disabled": station.get("num_docks_disabled", 0),
                "num_bikes_available": station.get("num_bikes_available", 0),
                "num_bikes_disabled": station.get("num_bikes_disabled", 0)
            }
            for station in stations
        ]

        return stations_data

    except requests.exceptions.RequestException as err:
        print(f"Error fetching bike station status information: {err}")
        return None


# Function to save data to JSON
def save_to_json(data, filename):
    """Save the data to a JSON file in the Data folder."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "Data")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    file_path = os.path.join(data_dir, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"{filename} JSON created and stored at: {file_path}")


# Function that runs every 5 minutes
def fetch_data():
    """Fetch and save data from APIs."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    print(f"[{timestamp}] Fetching and saving data...")  

    stations_info = fetch_bike_station_information()
    if stations_info:
        save_to_json(stations_info, "stations.json")

    stations_status = fetch_bike_station_status()
    if stations_status:
        save_to_json(stations_status, "stations_status.json")

    weather = fetch_weather_data()
    if weather:
        save_to_json(weather, "weather.json")


if __name__ == "__main__":

    fetch_data()
    
    # Schedule the fetch_data to run every 5 minutes
    schedule.every(5).minutes.do(fetch_data)

    print("Scheduler started. Fetching data every 5 minutes...")

    # Keep the script running indefinitely
    while True:
        schedule.run_pending()
        time.sleep(1)
