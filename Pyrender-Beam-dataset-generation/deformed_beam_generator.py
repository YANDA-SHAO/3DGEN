import json
import numpy as np
import pandas as pd
import trimesh
from utils import *


def generate_deformed_meshes(beam_type='cantilever',
                             mesh_meta_path="./base_beams/mesh_meta.xlsx",
                             output_dir="./deformed_beam",
                             num_meshes=5,
                             youngs_modulus=69000000000,
                             max_displacement=-0.03,
                             min_displacement=0.03,
                             locations=[0.9, 0.1]):
    """
       Generate deformed meshes of beams based on provided parameters. This function can be
       utilized to deform both simple support beams and cantilevers. The deformation is calculated
       based on given parameters like load, material properties, and beam geometry. The resulting
       deformed meshes are saved to the specified directory.

       Args:
       - beam_type (str): Specifies the type of the beam. It can be either 'simple_support' or 'cantilever'.
                         Determines which deformation model will be used.

       - mesh_meta_path (str): Path to the Excel file containing metadata about the base meshes.
                               This metadata includes properties like width, height, and file path.

       - output_dir (str): The directory where the deformed mesh files will be saved.

       - num_meshes (int): The number of mesh files to generate between the minimum and maximum displacements.

       - youngs_modulus (float): Modulus of elasticity of the material, typically in Pascals. Represents the
                                 material's stiffness.

       - max_displacement (float): Maximum displacement (in meters) for force estimation. It's the maximum
                                   deformation the beam should undergo.

       - min_displacement (float): Minimum displacement (in meters) for force estimation. It's the minimum
                                   deformation the beam should undergo.

       - locations (list): A list of load locations on the beam, represented as fractions of the beam length.
                           Determines where the force is applied on the beam.

       Returns:
       - str: Path to the JSON file containing metadata about the deformed beams, including the path
              to the mesh file, the modulus of elasticity used, and the moment of inertia.
       """

    assert beam_type in ['simple_support', 'cantilever'], "Invalid beam_type. Choose 'simple_support' or 'cantilever'."

    mesh_meta = pd.read_excel(mesh_meta_path)
    os.makedirs(output_dir, exist_ok=True)
    deformed_info = {}

    for _, example in mesh_meta.iterrows():
        moment_inertia = example.Height * (example.Width ** 3) / 12
        location_info = {}

        for loc in locations:
            if beam_type == 'simple_support':
                max_force = simple_support_beam_force_estimation(1, max_displacement, youngs_modulus, moment_inertia,
                                                                 loc)
                min_force = simple_support_beam_force_estimation(1, min_displacement, youngs_modulus, moment_inertia,
                                                                 loc)
            else:  # For 'cantilever'
                max_force = cantilever_power_estimation(1, max_displacement, youngs_modulus, moment_inertia)
                min_force = cantilever_power_estimation(1, min_displacement, youngs_modulus, moment_inertia)

            forces = np.linspace(min_force, max_force, num_meshes)
            power_info = {}

            for force in forces:
                beam = trimesh.load_mesh(example.Path)

                if beam_type == 'simple_support':
                    deformed_beam = simple_support_beam(beam, force, loc, youngs_modulus, moment_inertia)
                else:  # For 'cantilever'
                    deformed_beam = cantilever(beam, force, youngs_modulus, moment_inertia, 1)  # Assuming length = 1
                N_deformed_beam = normalize_mesh(deformed_beam)

                deformed_mesh_path = f"{output_dir}/{beam_type}_beam{loc}_{force}.obj"
                N_deformed_beam.export(deformed_mesh_path, file_type="obj")

                deformed_beam_info = {
                    "Path": deformed_mesh_path,
                    "E": youngs_modulus,
                    "I": moment_inertia
                }
                power_info[abs(force)] = deformed_beam_info

            location_info[loc] = power_info

        deformed_info[example.Name] = location_info

    json_path = os.path.join(output_dir, "deformed_info.json")
    with open(json_path, "w") as json_file:
        json.dump(deformed_info, json_file)

    print("Deformed beam information saved as JSON file:", json_path)
    return json_path

generate_deformed_meshes()