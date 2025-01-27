import plotly.graph_objects as go
from stl import mesh
import numpy as np

def render_stl(file_path):
    """Render an STL file using Plotly."""
    # Load the STL file
    stl_model = mesh.Mesh.from_file(file_path)

    # Extract vertices and faces
    vertices = stl_model.vectors.reshape(-1, 3)  # Flattened vertices
    faces = np.arange(len(vertices)).reshape(-1, 3)  # Indices for triangles

    # Create a Plotly mesh plot
    fig = go.Figure(
        data=[
            go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=faces[:, 0],  # Indices of the first vertex of each face
                j=faces[:, 1],  # Indices of the second vertex of each face
                k=faces[:, 2],  # Indices of the third vertex of each face
                color='lightblue',  # Set model color
                opacity=0.50,  # Transparency
            )
        ]
    )

    # Customize the scene layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(backgroundcolor="rgb(200, 200, 230)"),
            yaxis=dict(backgroundcolor="rgb(230, 200,200)"),
            zaxis=dict(backgroundcolor="rgb(200, 230,200)"),
        ),
        margin=dict(r=10, l=10, b=10, t=10),  # Reduce margins
    )

    # Show the figure
    fig.show()

# Example usage
if __name__ == "__main__":
    stl_file_path = "Wellnesscenter.stl"  # Replace with the path to your STL file
    render_stl(stl_file_path)
