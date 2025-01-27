import requests
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import streamlit as st

# --- Add your NASA API Key here ---
API_KEYS = {
    "nasa_earth": "key"  # Replace with your NASA API Key  
}

ENDPOINTS = {
    "nasa_earth": "key"
}

# --- Function to Fetch NASA Earth Imagery (DEM Data) ---
def fetch_dem_data(lat, lon, date="2021-07-01", dim=0.1, output_file="dem.tif"):
    """
    Fetch DEM data from NASA Earth API.
    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
        date: Date of the imagery to fetch (optional).
        dim: The dimension of the area to retrieve.
        output_file: The file path to save the DEM data.
    Returns:
        output_file: Path to the saved DEM file.
    """
    url = f"{ENDPOINTS['nasa_earth']}?lon={lon}&lat={lat}&dim={dim}&date={date}&api_key={API_KEYS['nasa_earth']}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return output_file
    else:
        st.error(f"NASA API Error: {response.status_code} - {response.text}")
        raise ValueError(f"NASA API Error: {response.status_code} - {response.text}")

# --- Function to Calculate Slope and Aspect ---
def calculate_slope_aspect(dem_array, resolution):
    """
    Calculate the slope and aspect of a DEM.
    Args:
        dem_array: 2D array of elevation values.
        resolution: The spatial resolution of the DEM (in meters).
    Returns:
        slope: 2D array representing slope in radians.
        aspect: 2D array representing aspect in radians.
    """
    # Calculate gradients in x and y directions
    x, y = np.gradient(dem_array, resolution)

    # Calculate slope
    slope = np.sqrt(x**2 + y**2 + 1e-6)  # Add a small value to avoid division by zero

    # Calculate aspect
    aspect = np.arctan2(-y, x)  # Negative y to match compass directions
    return slope, aspect

# --- Visualization Function ---
def visualize_slope(slope):
    """
    Visualize the slope map in Streamlit.
    Args:
        slope: 2D array representing slope in radians.
    """
    # Convert slope to degrees for easier interpretation
    slope_degrees = np.degrees(slope)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Set plot size
    cax = ax.imshow(slope_degrees, cmap="gray", norm=Normalize(vmin=0, vmax=30))  # Background gray-scale slope
    fig.colorbar(cax, label="Slope (degrees)")
    ax.set_title("Slope Map")
    ax.axis("off")

    # Display the plot in Streamlit
    st.pyplot(fig)  # Streamlit method to display the plot

# --- Main Function ---
def slope_complete(lat, lon):
    """
    Complete function to fetch DEM data, calculate slope, and visualize it.
    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
    """
    try:
        # Fetch DEM data from NASA Earth API
        dem_file = fetch_dem_data(lat=lat, lon=lon)
        st.write(f"Fetched DEM data: {dem_file}")
        
        # Load DEM data
        with rasterio.open(dem_file) as dem:
            dem_data = dem.read(1)  # Read the first band (elevation)
            resolution = dem.res[0] if hasattr(dem, "res") else 1.0  # Ensure resolution is valid

        # Handle missing or invalid values in the DEM
        dem_data = np.nan_to_num(dem_data, nan=0.0)

        # Calculate slope and aspect
        slope, aspect = calculate_slope_aspect(dem_data, resolution)

        # Visualize the slope map
        visualize_slope(slope)

        # Optionally, allow user to download the DEM data
        with open(dem_file, "rb") as f:
            st.download_button(label="Download DEM Data", data=f, file_name="dem_data.tif", mime="application/tiff")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
