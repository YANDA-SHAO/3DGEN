import numpy as np
import pandas as pd
from analytic_functions import beam_generator


# Define function to generate beam meshes and metadata
def generate_beam_meshes(num_widths=10, num_heights=10, start_width=0.02, end_width=0.1, min_height_ratio=0.15,
                         max_height_ratio=1.2):
    # Generate width values
    widths = [start_width - (i / (num_widths - 1)) ** 0.85 * (start_width - end_width) for i in range(num_widths)]

    # Generate height ratio values
    height_ratios = np.linspace(min_height_ratio, max_height_ratio, num_heights)

    # Create dictionary mapping each width to its corresponding heights
    width_height_dict = {width: [width * height_ratio for height_ratio in height_ratios] for width in widths}

    # Initialize mesh metadata matrix
    mesh_meta = np.empty((num_widths * num_heights, 3))

    # Fill metadata matrix with length, width, and height of each beam
    for i, width in enumerate(widths):
        heights = width_height_dict[width]
        mesh_meta[i * num_heights: (i + 1) * num_heights] = np.column_stack(
            (np.ones(num_heights), np.full(num_heights, width), heights))

    # Swap the width and height columns for correct formatting
    mesh_meta[:, [1, 2]] = mesh_meta[:, [2, 1]]

    # Generate beam meshes and save as .obj files
    for i, shape in enumerate(mesh_meta):
        beam = beam_generator(shape)
        filename = f'./base_beams/beam_{i:04d}.obj'
        beam.export(filename, file_type='obj')

    # Create DataFrame of beam metadata
    beam_names = [f"beam_{i:04d}" for i in range(num_widths * num_heights)]
    beam_paths = [f"./base_beams/beam_{i:04d}.obj" for i in range(num_widths * num_heights)]
    df = pd.DataFrame({"Name": beam_names, "Path": beam_paths, "Length": mesh_meta[:, 0], "Height": mesh_meta[:, 1],
                       "Width": mesh_meta[:, 2]})
    df = df[["Name", "Path", "Length", "Height", "Width"]]

    # Save DataFrame to Excel
    df.to_excel("./base_beams/mesh_meta.xlsx", index=False)

    print(f"Successfully generated {num_widths * num_heights} beam meshes and saved metadata to ./beams/mesh_meta.xlsx")


# Call function to generate beam meshes
generate_beam_meshes()
