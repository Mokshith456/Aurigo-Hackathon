import React, { useState } from "react";
import { MapContainer, TileLayer, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";

function LocationMarker({ setCoordinates }) {
    useMapEvents({
        click(e) {
            const { lat, lng } = e.latlng;
            setCoordinates({ lat, lng });
        },
    });

    return null;
}

function App() {
    const [coordinates, setCoordinates] = useState(null);
    const [inputCoordinates, setInputCoordinates] = useState({ lat: "", lng: "" });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setInputCoordinates({ ...inputCoordinates, [name]: value });
    };

    const submitCoordinates = async () => {
        const data = coordinates || inputCoordinates;
        const response = await fetch("http://localhost:5000/store-coordinates", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        const result = await response.json();
        alert(`Coordinates saved: ${JSON.stringify(result)}`);
    };

    return (
        <div>
            <h1>World Map Coordinates</h1>
            <MapContainer
                center={[20, 0]}
                zoom={2}
                style={{ height: "400px", width: "100%" }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                <LocationMarker setCoordinates={setCoordinates} />
            </MapContainer>
            <div>
                <h3>Selected Coordinates:</h3>
                {coordinates && (
                    <p>
                        Latitude: {coordinates.lat}, Longitude: {coordinates.lng}
                    </p>
                )}
            </div>
            <div>
                <h3>Enter Coordinates Manually:</h3>
                <input
                    type="text"
                    name="lat"
                    placeholder="Latitude"
                    value={inputCoordinates.lat}
                    onChange={handleInputChange}
                />
                <input
                    type="text"
                    name="lng"
                    placeholder="Longitude"
                    value={inputCoordinates.lng}
                    onChange={handleInputChange}
                />
            </div>
            <button onClick={submitCoordinates}>Submit Coordinates</button>
        </div>
    );
}

export default App;

