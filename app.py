import streamlit as st
import time
# import rasterio
import folium
from streamlit_folium import st_folium
from terrain_gis import slope_complete  # Import the slope_complete function from terrain_gis.py
from dwg_ifc import dwg_ifc  # Import the dwg_ifc function from dwg_ifc.py
from risk_man import risk_man
from creat_recommed import create_recommend
from ifc_to_ifc import single_function, get_natural_calamities_data,display_txt_file,extract_and_save_ifc_contents,display_txt_file___
from STLModel import render_stl
import shutil
import os

global lat,long

# Initialize session state for page navigation if not already set
if "page" not in st.session_state:
    st.session_state.page = "Choose Location"
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# Page configuration
st.set_page_config(page_title="Enhance GIS & BIM", layout="wide")
st.title("Enhanced BIM from Analysing GIS Using LLM's")
#  st.subheader("Choose the point on the map")
# Create two columns for layout: one for the map and one for the coordinates display
col1, col2 = st.columns([4, 5])  # Map takes more space, coordinates on the right

# Initialize the map centered on New York City
m = folium.Map(location=[40.7128, -74.0060], zoom_start=2)

# Create a global variable to store the current marker
marker = None

# Function to handle click and update marker position
def update_marker(lat, lon):
    global marker, m
    
    # If a marker already exists, remove it
    if marker:
        m.remove_child(marker)
    
    # Add a new marker at the clicked position
    marker = folium.Marker([lat, lon], popup="New marker", icon=folium.Icon(icon='cloud', color='blue', icon_color='white'))
    marker.add_to(m)

# Sidebar for Navigation
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio("Go to", ["Choose Location", "GIS Report", "BIM Report"], index=0 if st.session_state.page == "Choose Location" else 1 if st.session_state.page == "GIS Report" else 2, key="nav")

# Set the current page in session state
st.session_state.page = page_selection

# Sidebar for choosing method of location input
location_method = st.sidebar.radio("How would you like to provide the coordinates?", ["Map Selection", "Enter Coordinates"])


# Handle different pages based on navigation
if st.session_state.page == "Choose Location":
    if location_method == "Map Selection":
        # Render the map in the left column
        with col1:
            st.write("Click anywhere on the map to get the coordinates of that point, or enter the coordinates manually.")
            output = st_folium(m, height=540, width=540)

        # Handle the click event and show coordinates in the right column
        if output['last_clicked'] is not None:
            coordinates = output['last_clicked']
            lat = coordinates['lat']
            lon = coordinates['lng']
            
            # Update marker position with new coordinates
            update_marker(lat, lon)

            # Display the coordinates in the right column
            with col2:
                st.subheader("Coordinates of the selected point:")
                st.write(f"Latitude: {lat}, Longitude: {lon}")
                
                # Add submit button to confirm the coordinates
                if st.button('Submit'):
                    st.success(f"Coordinates confirmed: Latitude = {lat}, Longitude = {lon}")
                    # Store the coordinates in session state to pass to GIS Report
                    st.session_state.lat = lat
                    st.session_state.lon = lon
                    # Delay before showing the next part
                    time.sleep(3)
                    # Redirect to the next page
                    st.session_state.page = "GIS Report"
                    st.rerun()

    elif location_method == "Enter Coordinates":
        # User manually enters coordinates
        with col1:
            lat_input = st.number_input("Enter Latitude:", format="%.6f", min_value=-90.0, max_value=90.0)
            lon_input = st.number_input("Enter Longitude:", format="%.6f", min_value=-180.0, max_value=180.0)

            if lat_input and lon_input:
                # Update the map and marker with the manually entered coordinates
                update_marker(lat_input, lon_input)
                
                # Display the coordinates in the right column
                st.subheader("Coordinates you entered:")
                st.write(f"Latitude: {lat_input}, Longitude: {lon_input}")
                
                # Add submit button to confirm the coordinates
                if st.button('Submit'):
                    st.success(f"Coordinates confirmed: Latitude = {lat_input}, Longitude = {lon_input}")
                    # Store the coordinates in session state to pass to GIS Report
                    st.session_state.lat = lat_input
                    st.session_state.lon = lon_input
                    # Delay before showing the next part
                    time.sleep(1)
                    # Redirect to the next page
                    st.session_state.page = "GIS Report"
                    st.rerun()

elif st.session_state.page == "GIS Report":
    if not st.session_state.file_uploaded:
        # File uploader (only appears if file hasn't been uploaded)
        st.subheader("Upload your .dwg file to begin")
        uploaded_file = st.file_uploader("Choose a DWG file", type=["dwg"])

        if uploaded_file is not None:
            # Save the file to a folder
            save_path = os.path.join("uploaded_files", uploaded_file.name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Update session state to indicate file upload
            st.session_state.file_uploaded = True

            # Hide the uploader and display confirmation message
            st.success(f"File {uploaded_file.name} uploaded successfully.")
            dwg_ifc(save_path)  # Call the dwg_ifc function to convert the DWG file to IFC
            time.sleep(2)  # Wait before redirecting to the next part
            st.rerun()  # Reload the page to show the rest of the content

    else:
        # Create three columns for the GIS Report
        col1, col2= st.columns([2, 2])

        with col1:
            
            latitude = st.session_state.get("lat", None)
            longitude = st.session_state.get("lon", None)
            st.subheader("Slope Map")
            slope_complete(latitude, longitude)  # Pass lat and lon from session_state
            
        with col2:
            st.subheader("Disaster and Risk Management Map")
            st.write("This Map identifies flood and drought risks based on your location using OpenCage and OpenWeatherMap APIs.")
            latitude = st.session_state.get("lat", None)
            longitude = st.session_state.get("lon", None)
            risk_man(latitude,longitude)
            time.sleep(4)
     
        col1, col2= st.columns([2, 2])
        with col1:
            create_recommend("result_bridge.ifc",st.session_state.lat,st.session_state.lon)
            st.write("#### GIS Report:")
            display_txt_file("gis_report.txt")

        with col2:
            data = get_natural_calamities_data(latitude, longitude)
            st.write("#### Historical Natural Calamities Data:")
            st.write(data)
            st.write("----------------------------------------------- ")
            display_txt_file("recommendations.txt")
        
        time.sleep(2)
        single_function()

elif st.session_state.page == "BIM Report":
        col1, col2= st.columns([2, 2])
        with col1:
            st.write("#### Original IFC code:")
            extract_and_save_ifc_contents("result_bridge.ifc", "original_ifc.txt")
            display_txt_file___("original_ifc.txt")
            if st.button("Visulaize the BIM Model"):
                render_stl("Wellnesscenter.stl")

        with col2:
            st.write("#### IFC Code Updated with Recommendations:")
            extract_and_save_ifc_contents("output_file.ifc", "updated_ifc.txt")
            display_txt_file___("updated_ifc.txt")