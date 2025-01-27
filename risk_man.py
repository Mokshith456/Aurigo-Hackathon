import requests
import folium
from streamlit_folium import st_folium
import streamlit as st

# API keys and endpoints
opencage_api_key = "key"
openweather_api_key = "key"
opencage_url = "key"
openweather_url = "key"

# Function to get location details from OpenCage
def get_location_details(lat, lon):
    params = {
        "q": f"{lat},{lon}",
        "key": opencage_api_key
    }
    response = requests.get(opencage_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["formatted"]
    return "Unknown location"

# Function to get weather data from OpenWeatherMap
def get_weather_data(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": openweather_api_key,
        "units": "metric"
    }
    response = requests.get(openweather_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def risk_man(latitude,longitude):
    # Check if latitude and longitude are entered
    if latitude and longitude:
        try:
            lat = float(latitude)
            lon = float(longitude)

            # Get location details
            location = get_location_details(lat, lon)

            # Get weather data
            weather_data = get_weather_data(lat, lon)

            if weather_data:
                temp = weather_data["main"]["temp"]
                humidity = weather_data["main"]["humidity"]
                precipitation = weather_data.get("rain", {}).get("1h", 0)

                # Determine risk factors
                flood_risk = "High" if precipitation > 10 else "Low"
                drought_risk = "High" if humidity < 30 and precipitation == 0 else "Low"

                # Display results
                st.write(f"#### Location: {location}")
                st.write(f"Temperature: {temp}°C,  Humidity: {humidity}%, Flood Risk: {flood_risk},  Drought Risk: {drought_risk}")

                # Create a map
                m = folium.Map(location=[lat, lon], zoom_start=10)
                folium.Marker(
                    location=[lat, lon],
                    popup=(
                        f"<b>Location:</b> {location}<br>"
                        f"<b>Temperature:</b> {temp}°C<br>"
                        f"<b>Humidity:</b> {humidity}%<br>"
                        f"<b>Flood Risk:</b> {flood_risk}<br>"
                        f"<b>Drought Risk:</b> {drought_risk}"
                    ),
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

                # Display the map
                st_folium(m, width=500, height=500)
            else:
                st.error("Failed to retrieve weather data. Please check your API key or inputs.")

        except ValueError:
            st.error("Invalid latitude or longitude. Please enter valid numeric values.")
    else:
        st.info("Please enter latitude and longitude to get started.")