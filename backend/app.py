from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import aspose.cad as cad
from aspose.cad import Color
from aspose.cad.imageoptions import IfcOptions
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

UPLOAD_FOLDER = './upload'
CONVERTED_FOLDER = './converted'
GLTF_FOLDER = './gltf'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(GLTF_FOLDER, exist_ok=True)

def convert_dwg_to_ifc(input_file, output_file):
    try:
        # Load the DWG file
        image = cad.Image.load(input_file)

        # Configure rasterization options
        cadRasterizationOptions = cad.imageoptions.CadRasterizationOptions()
        cadRasterizationOptions.page_height = 800.5
        cadRasterizationOptions.page_width = 800.5
        cadRasterizationOptions.zoom = 1.5
        cadRasterizationOptions.layers = "Layer"  # Specify the layer to use
        cadRasterizationOptions.background_color = Color.green

        # Configure IFC export options
        options = IfcOptions()
        options.vector_rasterization_options = cadRasterizationOptions

        # Save to IFC format
        image.save(output_file, options)
        print(f"Conversion successful! IFC file saved as {output_file}")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        raise e

def convert_ifc_to_gltf(ifc_file, gltf_file):
    try:
        # Use IfcConvert from IfcOpenShell to convert IFC to GLTF
        subprocess.run(["IfcConvert", ifc_file, gltf_file], check=True)
        
        # Check if the GLTF file was created successfully
        if os.path.exists(gltf_file):
            print(f"Conversion successful! GLTF file saved as {gltf_file}")
        else:
            raise FileNotFoundError(f"GLTF file not created: {gltf_file}")

    except Exception as e:
        print(f"An error occurred during IFC to GLTF conversion: {e}")
        raise e


@app.route('/')
def home():
    return "Backend is running!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.dwg'):
        return jsonify({'error': 'Only DWG files are supported'}), 400

    # Save the uploaded DWG file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Output paths for IFC and GLTF files
        output_ifc = os.path.join(CONVERTED_FOLDER, os.path.splitext(file.filename)[0] + '.ifc')
        output_gltf = os.path.join(GLTF_FOLDER, os.path.splitext(file.filename)[0] + '.gltf')

        # Convert DWG to IFC
        convert_dwg_to_ifc(file_path, output_ifc)

        # Convert IFC to GLTF
        convert_ifc_to_gltf(output_ifc, output_gltf)

        return jsonify({
            'message': 'File converted successfully',
            'ifc_file': os.path.basename(output_ifc),
            'gltf_file': os.path.basename(output_gltf),
            'download_url': f'/download/{os.path.basename(output_ifc)}'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if filename.endswith('.ifc'):
        file_path = os.path.join(CONVERTED_FOLDER, filename)
    elif filename.endswith('.gltf'):
        file_path = os.path.join(GLTF_FOLDER, filename)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
