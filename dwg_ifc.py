from aspose.cad import Image, Color
from aspose.cad.imageoptions import CadRasterizationOptions, IfcOptions # Correct import for Color

def dwg_ifc(input_file):
    # Set up CAD rasterization options
    image = Image.load(input_file)  # Directly use 'Image' from aspose.cad
    cadRasterizationOptions = CadRasterizationOptions()  # Correct initialization of CadRasterizationOptions
    cadRasterizationOptions.page_height = 800.5
    cadRasterizationOptions.page_width = 800.5
    cadRasterizationOptions.zoom = 1.5
    cadRasterizationOptions.layers = ["Layer"]  # Ensure layers are provided as a list
    cadRasterizationOptions.background_color = Color.green  # Set background color to green

    # Set up IFC options
    options = IfcOptions()  # Directly use IfcOptions from aspose.cad.imageoptions
    options.vector_rasterization_options = cadRasterizationOptions

    # Save the image as an IFC file
    image.save("result_bridge.ifc", options)
