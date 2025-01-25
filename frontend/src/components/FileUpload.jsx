import React, { useState } from "react";
import axios from "axios";
import "../App.css"; // Correct relative path for the CSS file

function FileUpload() {
  const [file, setFile] = useState(null);
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [elevation, setElevation] = useState("");
  const [progress, setProgress] = useState("");
  const [ifcFile, setIfcFile] = useState(null);
  const [gltfFile, setGltfFile] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file || !lat || !lng || !elevation) {
      alert("Please provide all required fields.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("lat", lat);
    formData.append("lng", lng);
    formData.append("elevation", elevation);

    try {
      setProgress("Uploading and processing file...");

      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setIfcFile(response.data.ifc_file);
      setGltfFile(response.data.gltf_file);
      setProgress("File processed successfully! Download options are available below.");
    } catch (error) {
      console.error("Error uploading file:", error);
      setProgress("Error processing file. Please try again.");
    }
  };

  const handleIfcDownload = () => {
    if (ifcFile) {
      window.location.href = `http://127.0.0.1:5000/download/${ifcFile}`;
    } else {
      alert("No IFC file available for download.");
    }
  };

  const handleGltfDownload = () => {
    if (gltfFile) {
      window.location.href = `http://127.0.0.1:5000/download/${gltfFile}`;
    } else {
      alert("No GLTF file available for download.");
    }
  };

  return (
    <div className="App">
      <h1>BIM + GIS Integration</h1>

      <form onSubmit={handleUpload}>
        <div>
          <label htmlFor="file">Upload 2D AutoCAD (.dwg) file:</label>
          <input type="file" id="file" onChange={handleFileChange} />
        </div>

        <div>
          <label htmlFor="lat">Latitude:</label>
          <input
            type="text"
            id="lat"
            value={lat}
            onChange={(e) => setLat(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="lng">Longitude:</label>
          <input
            type="text"
            id="lng"
            value={lng}
            onChange={(e) => setLng(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="elevation">Elevation:</label>
          <input
            type="text"
            id="elevation"
            value={elevation}
            onChange={(e) => setElevation(e.target.value)}
          />
        </div>

        <button type="submit">Upload and Process</button>
      </form>

      {progress && <p>{progress}</p>}

      {ifcFile && (
        <button onClick={handleIfcDownload}>Download Processed IFC File</button>
      )}
      {gltfFile && (
        <button onClick={handleGltfDownload}>Download Processed GLTF File</button>
      )}
    </div>
  );
}

export default FileUpload;

