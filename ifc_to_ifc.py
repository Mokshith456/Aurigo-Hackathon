import openai
import ifcopenshell
import os
import streamlit as st


def extract_and_save_ifc_contents(ifc_file_path, txt_file_path):
    # Load the .ifc file using ifcopenshell
    ifc_file = ifcopenshell.open(ifc_file_path)
    
    # Prepare to store the extracted content
    content = []

    # Iterate through all elements in the .ifc file and add them to the content list
    for element in ifc_file:
        content.append(str(element))  # Convert each element to string for easy representation

    # Save the extracted content to a .txt file
    with open(txt_file_path, 'w') as file:
        file.write("\n".join(content))
    
    print(f"Content saved to {txt_file_path}")


openai.api_key = 'key'
def generate_ifc_code_from_file(input_file_path, output_file_path):
    # Function to read input from file
    def read_input_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    # Function to write the output to a new file
    def write_output_file(file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)

    # Define the prompt to send to the GPT-4 model
    def generate_ifc_code(input_text):
        messages = [
            {"role": "system", "content": "You are a helpful assistant that converts building recommendations into IFC code format."},
            {"role": "user", "content": f"""
            I have a set of building recommendations based on a BIM model. 
            Please convert these recommendations into the IFC code format using the following structure:

            - Each building element should be represented by 'IfcBuildingElementProxy' with a unique GUID.
            - Add properties such as insulation type, window type, HVAC system, material type, reinforcement, etc., based on the recommendations.
            - Ensure to follow the IFC structure with property definitions, relationships, and placements as needed.

            Here are the building recommendations:

            {input_text}

            this is the format of the Output the IFC code format as follows:

            #1=IfcBuildingElementProxy('guid',$,$,$,$,#14,#16,$,$)
            #2=IfcPropertySingleValue('PropertyName',$,.STRING.,'PropertyValue')
            #3=IfcRelDefinesByProperties($,$,$,#1,(#2))
            """}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1500,
            temperature=0.5
        )

        return response['choices'][0]['message']['content'].strip()

    # Main process
    # Read input, generate IFC code, and write to output file
    recommendations_text = read_input_file(input_file_path)
    ifc_code = generate_ifc_code(recommendations_text)
    write_output_file(output_file_path, ifc_code)

    print(f"IFC code has been successfully written to {output_file_path}.")


def extract_lines_with_hash(input_file_path, output_file_path):
    # Function to read input file, filter lines starting with '#', and write them to an output file
    with open(input_file_path, 'r') as infile:
        lines = infile.readlines()

    # Filter lines that start with '#'
    lines_with_hash = [line for line in lines if line.startswith('#')]

    # Write the filtered lines to a new output file
    with open(output_file_path, 'w') as outfile:
        outfile.writelines(lines_with_hash)

    print(f"Filtered lines have been written to {output_file_path}.")



def stitch_and_adjust_numbering(file1_path, file2_path, output_file_path):
    # Function to read a file and return its lines
    def read_file(file_path):
        with open(file_path, 'r') as file:
            return file.readlines()

    # Read both files
    lines_file1 = read_file(file1_path)
    lines_file2 = read_file(file2_path)

    # Find the last number after '#' in the first file
    last_number_file1 = 0
    for line in lines_file1:
        if line.startswith('#'):
            parts = line.split('=')
            number = parts[0].strip('#').strip()
            try:
                last_number_file1 = max(last_number_file1, int(number))
            except ValueError:
                continue

    # Adjust the numbering in the second file
    adjusted_lines_file2 = []
    for line in lines_file2:
        if line.startswith('#'):
            parts = line.split('=')
            number = parts[0].strip('#').strip()
            try:
                # Increment the number based on the last number from file 1
                new_number = last_number_file1 + 1
                last_number_file1 = new_number
                # Update the line with the new number
                new_line = f"#{new_number}={parts[1]}"
                adjusted_lines_file2.append(new_line)
            except IndexError:
              continue
            except ValueError:
                continue
        else:
            adjusted_lines_file2.append(line)

    # Merge the lines and remove any '[' characters
    all_lines = lines_file1 + ["\n"] + adjusted_lines_file2
    all_lines = [line.replace('[', '') for line in all_lines]

    # Write the merged content into the output file
    with open(output_file_path, 'w') as outfile:
        outfile.writelines(all_lines)

    print(f"Files have been stitched, and '[' has been removed. The result is saved in {output_file_path}.")



def convert_txt_to_ifc_and_cleanup(input_txt_file, output_ifc_file, files_to_delete):
    # Define the header content for the IFC file
    header_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Created by Aspose.CAD'),'2;1');
FILE_NAME('Aspose.CAD','2025-01-25T11:50:44',('Aspose'),('Aspose'),'','','');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;
DATA;
"""

    # Step 5: Convert the .txt file to a .ifc file
    with open(input_txt_file, 'r') as txt_file:
        content = txt_file.read()

    # Combine the header and the content
    full_content = header_content + content

    # Write the combined content into a new .ifc file
    with open(output_ifc_file, 'w') as ifc_file:
        ifc_file.write(full_content)

    print(f"IFC file has been successfully created: {output_ifc_file}")

    # Step 6: Delete extra files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"Error in deletion: {file_path}")

    print("Step 6 Done")

def single_function():
  extract_and_save_ifc_contents("result_bridge.ifc", "output.txt")
  generate_ifc_code_from_file("recommendations.txt", "ifc_code_output.txt")
  extract_lines_with_hash("ifc_code_output.txt","filtered_output.txt")
  stitch_and_adjust_numbering("output.txt", "filtered_output.txt", "final_output.txt")
  files_to_delete = [
      'filtered_output.txt',
      'final_output.txt',
      'generated_output.txt',
      'ifc_code_output.txt',
      'output.txt'
  ]
  convert_txt_to_ifc_and_cleanup("final_output.txt", "output_file.ifc", files_to_delete)
  

def get_natural_calamities_data(lat, long):
    # The prompt to get the historic calamity data
    prompt = f"list out the historic data and if any possible calamiies that may occur in the near future ad the location with latitude {lat} and longitude {long} it doesnt have to be a perfect prediction it can be basic and just a pissible suggestion"

    # Make the request to OpenAI's API
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can change the model version if needed
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250,  # Adjust token length if needed
        temperature=0.7  # Adjust the creativity of the response
    )
    
    return response['choices'][0]['message']['content'].strip()

def display_txt_file(file_path):
    # Read the content of the .txt file
    with open(file_path, 'r') as file:
        content = file.read()
    st.write(content)
    
def display_txt_file___(file_path):
    # Read the content of the .txt file
    with open(file_path, 'r') as file:
        content = file.read()
    st.text(content) 