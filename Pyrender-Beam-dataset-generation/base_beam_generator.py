import numpy as np
import pandas as pd
from utils import beam_generator
import os
def generate_beam_meshes(output_dir="./base_beams",
                         split = 4,
                         num_heights=3, num_widths=3, start_height=0.02,
                         end_height=0.05, min_width_ratio=1, max_width_ratio=2):
    """
    Generate a set of beam meshes based on specified parameters. The function creates 3D models of beams
    with varying heights and widths, exports them as .obj files, and then saves the metadata for each
    generated beam in an Excel spreadsheet.

    Args:
    - output_dir (str): Directory where the generated .obj files and Excel metadata file will be saved.
    - num_heights (int): Number of distinct beam heights.
    - num_widths (int): Number of distinct beam widths for each height.
    - start_height (float): Minimum beam height.
    - end_height (float): Maximum beam height.
    - min_width_ratio (float): Minimum width as a ratio of the height.
    - max_width_ratio (float): Maximum width as a ratio of the height.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Compute the heights for the beams using a non-linear function for diversity.
    heights = [start_height - (i / (num_heights - 1)) ** 0.85 * (start_height - end_height) for i in range(num_heights)]

    # Calculate corresponding widths for each height by multiplying with a set of width ratios.
    widths = np.outer(heights, np.linspace(min_width_ratio, max_width_ratio, num_widths))

    # Initialize a list to store metadata about each generated beam.
    beam_data = []

    # Iterate over each combination of height and width.
    for i, height in enumerate(heights):
        for j, width in enumerate(widths[i]):
            # Assume a fixed length of 1 for simplicity. Can be modified if needed.
            shape = (1, height, width)

            # Use the utility function to generate the 3D mesh for the beam.
            beam = beam_generator(shape, split)

            # Define the filename to store the beam's 3D model.
            filename = f'{output_dir}/beam_{i * num_widths + j:04d}.obj'

            # Export the 3D model of the beam to the specified filename.
            beam.export(filename, file_type='obj')

            # Append the metadata of the current beam to the beam_data list.
            beam_data.append([f"beam_{i * num_widths + j:04d}", filename, 1, height, width])

    # Convert the list of metadata into a DataFrame for easier manipulation and storage.
    df = pd.DataFrame(beam_data, columns=["Name", "Path", "Length", "Height", "Width"])

    # Save the metadata into an Excel file in the specified directory.
    df.to_excel(f"{output_dir}/mesh_meta.xlsx", index=False)

    print(
        f"Successfully generated {num_heights * num_widths} beam meshes and saved metadata to {output_dir}/mesh_meta.xlsx")


# Execute the function to generate the beam meshes.
generate_beam_meshes()
