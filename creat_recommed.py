import ifcopenshell
import requests
from groq import Groq
import streamlit as st

# --- Add your API Keys and Endpoints here ---
API_KEYS = {
    "opencage": "key",
    "openweathermap": "key",
    "nasa_earth": "key",
    "llama": "key"
}

ENDPOINTS = {
    "opencage": "key",
    "nasa_earth": "key",
    "openweathermap": "key",
    "openweather_air_quality": "key"
}

# --- Function to Get Coordinates ---
def get_coordinates(lat,lng):
    url = f"{ENDPOINTS['opencage']}?q={lat},{lng}&key={API_KEYS['opencage']}"
    response = requests.get(url).json()
    if response['results']:
        coordinates = response['results'][0]['geometry']
        return coordinates['lat'], coordinates['lng']
    return None, None

# --- Function to Fetch Weather and Air Quality Data ---
def get_weather_and_air_quality(lat, lng):
    weather_url = f"{ENDPOINTS['openweathermap']}?lat={lat}&lon={lng}&appid={API_KEYS['openweathermap']}&units=metric"
    weather_response = requests.get(weather_url).json()
    if weather_response.get("cod") != 200:
        raise ValueError(f"Weather API error: {weather_response.get('message')}")

    weather_data = {
        "temperature": weather_response['main']['temp'],
        "feels_like": weather_response['main']['feels_like'],
        "humidity": weather_response['main']['humidity'],
        "pressure": weather_response['main']['pressure'],
        "wind_speed": weather_response['wind']['speed'],
        "weather_description": weather_response['weather'][0]['description'],
        "weather_main": weather_response['weather'][0]['main'],
        "visibility": weather_response['visibility'],
        "sunrise": weather_response['sys']['sunrise'],
        "sunset": weather_response['sys']['sunset']
    }

    air_quality_url = f"{ENDPOINTS['openweather_air_quality']}?lat={lat}&lon={lng}&appid={API_KEYS['openweathermap']}"
    air_quality_response = requests.get(air_quality_url).json()
    if air_quality_response.get("cod") != None and air_quality_response.get("cod") != 200:
        raise ValueError(f"Air Quality API error: {air_quality_response.get('message')}"
    )

    air_quality_data = air_quality_response['list'][0]['main']
    air_quality_components = air_quality_response['list'][0]['components']

    weather_data.update({
        "air_quality_index": air_quality_data['aqi'],
        "air_quality_components": air_quality_components
    })

    return weather_data

# --- Function to Fetch NASA Earth Imagery ---
def get_nasa_earth_imagery(lat, lng, date="2023-01-01", dim=0.1):
    url = f"{ENDPOINTS['nasa_earth']}?lat={lat}&lon={lng}&dim={dim}&date={date}&api_key={API_KEYS['nasa_earth']}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.url
    else:
        raise ValueError(f"NASA Earth API error: {response.status_code} - {response.text}")

# --- Function to Generate GIS Report using Llama ---
def generate_gis_report(lat,lng, weather_data, nasa_image_url):
    client = Groq(api_key=API_KEYS["llama"])
    prompt = f"""
    Generate a detailed GIS report for {lat} , {lng}. Include:
    - Weather: {weather_data['weather_description']}, temperature: {weather_data['temperature']}°C, feels like: {weather_data['feels_like']}°C, humidity: {weather_data['humidity']}%.
    - AQI: {weather_data['air_quality_index']}.
    - Air Quality Components: PM2.5: {weather_data['air_quality_components']['pm2_5']}, PM10: {weather_data['air_quality_components']['pm10']}.
    - Satellite Image: {nasa_image_url}.
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            # max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        report = ""
        for chunk in completion:
            report += chunk.choices[0].delta.content or ""
        return report.strip()
    except Exception as e:
        return f"Error generating report: {e}"

# --- Function to Generate BIM Recommendations from GIS ---
def generate_bim_recommendations_from_gis(gis_report, ifc_structure):
    client = Groq(api_key=API_KEYS["llama"])
    prompt = f"""
    You are an expert in Building Information Modeling (BIM). Based on the following GIS report and IFC structure, suggest specific changes to improve the building's BIM design:

    GIS Report:
    {gis_report}

    IFC Structure (simplified):
    {ifc_structure}

    Focus areas for improvement:
    1. Energy efficiency (e.g., insulation, window types, HVAC systems)
    2. Structural integrity (e.g., materials, reinforcements)
    3. Environmental resilience (e.g., flood resistance, green roofs)
    4. Compliance with weather conditions (e.g., cold temperatures, wind resistance)
    5. Air quality considerations (e.g., ventilation, filters).

    Provide actionable suggestions for the building elements in the IFC file.
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            # max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        recommendations = ""
        for chunk in completion:
            recommendations += chunk.choices[0].delta.content or ""
        return recommendations.strip()
    except Exception as e:
        return f"Error generating recommendations: {e}"

# --- Function to Analyze IFC File ---
def analyze_ifc_file(ifc_path):
    try:
        model = ifcopenshell.open(ifc_path)
    except Exception as e:
        # Read the first 100 bytes of the IFC file to examine the header/schema
        with open(ifc_path, 'rb') as f:
            header = f.read(100)
        raise ValueError(f"Error opening IFC file: {e}. File Header: {header}")
    structure = {}

    structure["elements"] = []
    for element in model.by_type("IfcBuildingElement"):
        structure["elements"].append({
            "type": element.is_a(),
            "name": element.Name,
            "guid": element.GlobalId,
            "properties": {prop.Name: prop.NominalValue.wrappedValue for prop in element.IsDefinedBy[0].RelatingPropertyDefinition.HasProperties} if element.IsDefinedBy else {}
        })
    return model, structure

# --- Function to Apply BIM Recommendations to IFC File ---
# def apply_bim_recommendations_to_ifc(ifc_model, recommendations):
#     changes = []
#     for rec in recommendations.split("\n"):
#         if "Add insulation" in rec:
#             guid = rec.split("GUID")[-1].strip()
#             element = ifc_model.by_guid(guid)
#             if element:
#                 changes.append(f"Added insulation to {element.Name} (GUID: {guid})")
#         elif "Reinforce" in rec:
#             guid = rec.split("GUID")[-1].strip()
#             element = ifc_model.by_guid(guid)
#             if element:
#                 changes.append(f"Reinforced {element.Name} (GUID: {guid})")
#     return changes

def create_recommend(ifc_path,lat,lng):
        if not lat or not lng:
            raise ValueError("Failed to fetch coordinates.")

        weather_data = get_weather_and_air_quality(lat, lng)
        nasa_image_url = get_nasa_earth_imagery(lat, lng)

        gis_report = generate_gis_report(lat,lng, weather_data, nasa_image_url)
        # print("GIS Report Generated:")
        # print(gis_report)

        with open("gis_report.txt", "w", encoding="utf-8") as gis_file:
            gis_file.write(gis_report)

        ifc_model, ifc_structure = analyze_ifc_file(ifc_path)

        recommendations = generate_bim_recommendations_from_gis(gis_report, ifc_structure)
        # print("BIM Recommendations Generated:")
        # print(recommendations)

        with open("recommendations.txt", "w") as rec_file:
            rec_file.write(recommendations)

        # changes = apply_bim_recommendations_to_ifc(ifc_model, recommendations)
        # print("Changes Applied to IFC File:")
        # print(changes)

        modified_ifc_path = "modified_" + ifc_path.split("/")[-1]
        ifc_model.write(modified_ifc_path)
        # print(f"Modified IFC file saved as '{modified_ifc_path}'")