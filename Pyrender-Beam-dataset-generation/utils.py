import trimesh
import numpy as np
import os
import json

def beam_generator(shape, split):
    """
    Generate a subdivided beam mesh based on the provided shape.

    Parameters:
    - shape (tuple): Dimensions of the box (length, width, height).

    Returns:
    - cantilever (Trimesh): Subdivided beam mesh.
    """

    # Create a box mesh based on the given shape and position it
    #position = shape / 2
    position = (shape[0] / 2, shape[1] / 2, shape[2] / 2)
    mesh = trimesh.creation.box(shape)
    beam = trimesh.Trimesh(vertices=mesh.vertices + position, faces=mesh.faces)

    # Subdivide the mesh multiple times for refinement
    for _ in range(split):
        beam = beam.subdivide()

    print('Number of vertices:', beam.vertices.shape[0])
    print('Number of faces:', beam.faces.shape[0])
    return beam


def cantilever(mesh, load, modulus_elasticity, moment_inertia, beam_length):
    """
    Modifies the given mesh to represent the deflection of a cantilevered beam
    under a point load at its free end.

    Parameters:
    - mesh (Trimesh): Initial beam mesh.
    - load (float): Point load at the free end of the cantilever.
    - modulus_elasticity (float): Modulus of elasticity of the material.
    - moment_inertia (float): Moment of inertia of the beam's cross-sectional area.
    - beam_length (float): Length of the cantilevered beam.

    Returns:
    - Trimesh: Mesh representing the deflected beam.
    """

    for vertex in mesh.vertices:
        x_distance = vertex[0]
        y_deflection = (load * x_distance ** 2 * (3 * beam_length - x_distance)) / (
                    6 * modulus_elasticity * moment_inertia)
        vertex[1] += y_deflection  # Apply the deflection to the y-coordinate of the vertex

    return mesh


def simple_support_beam(mesh, load, distance_from_support, modulus_elasticity, moment_inertia):
    """
    Modifies the given mesh to represent the deflection of a simply supported beam
    under a point load located at a specified distance from one of the supports.

    Parameters:
    - mesh (Trimesh): Initial beam mesh.
    - load (float): Point load applied on the beam.
    - distance_from_support (float): Distance from the left support to where the load is applied.
    - modulus_elasticity (float): Modulus of elasticity of the material.
    - moment_inertia (float): Moment of inertia of the beam's cross-sectional area.

    Returns:
    - Trimesh: Mesh representing the deflected beam.
    """

    L = 1  # Assuming the length of the beam is along the x-axis
    for vertex in mesh.vertices:
        x_distance = vertex[0]

        if x_distance < distance_from_support:
            y_deflection = (load * (L - distance_from_support) * x_distance *
                            (L ** 2 - x_distance ** 2 - (L - distance_from_support) ** 2)) / (
                                       6 * L * modulus_elasticity * moment_inertia)
        else:
            y_deflection = (load * distance_from_support * (L - x_distance) *
                            (L ** 2 - (L - x_distance) ** 2 - distance_from_support ** 2)) / (
                                       6 * L * modulus_elasticity * moment_inertia)

        vertex[1] += y_deflection  # Apply the deflection to the y-coordinate of the vertex

    return mesh


def cantilever_power_estimation(beam_length, tip_displacement, modulus_elasticity, moment_inertia):
    """
    Estimate the power (or force) for a cantilever based on its length,
    displacement at the free end, and material properties.

    Parameters:
    - beam_length (float): Length of the cantilevered beam.
    - tip_displacement (float): Displacement at the free end of the cantilever.
    - modulus_elasticity (float): Modulus of elasticity of the material.
    - moment_inertia (float): Moment of inertia of the beam's cross-sectional area.

    Returns:
    - int: Estimated power (or force).
    """

    power_estimate = int(
        (6 * beam_length * modulus_elasticity * moment_inertia * tip_displacement) / (beam_length ** 3))
    return power_estimate


def simple_support_beam_force_estimation(beam_length, displacement, modulus_elasticity, moment_inertia, load_location):
    """
    Estimate the force applied on a simply supported beam based on its length,
    displacement at a specific location, and material properties.

    Parameters:
    - beam_length (float): Length of the simply supported beam.
    - displacement (float): Displacement at the specified location on the beam.
    - modulus_elasticity (float): Modulus of elasticity of the material.
    - moment_inertia (float): Moment of inertia of the beam's cross-sectional area.
    - load_location (float): Location on the beam where the load is applied.

    Returns:
    - int: Estimated force.
    """

    force_estimate = int((6 * beam_length * modulus_elasticity * moment_inertia * displacement) /
                         (load_location * (beam_length - load_location) *
                          (beam_length ** 2 - (beam_length - load_location) ** 2 - load_location ** 2)))
    return force_estimate


import trimesh
import numpy as np


def mesh_stats(mesh):
    """
    Computes statistics of a Trimesh object's vertices and returns as {num,min,max,centroid}
    """
    vertices = mesh.vertices
    minVertex = np.min(vertices, axis=0)
    maxVertex = np.max(vertices, axis=0)
    centroid = np.mean(vertices, axis=0)
    numVertices = len(vertices)

    info = {'numVertices': numVertices, 'min': minVertex, 'max': maxVertex, 'centroid': centroid}
    return info


def normalize_mesh(input_mesh):
    """
    Normalize a given Trimesh object.

    Args:
    - input_mesh (Trimesh): The mesh to be normalized.

    Returns:
    - Trimesh: Normalized mesh.
    """
    stats = mesh_stats(input_mesh)
    diag = stats['max'] - stats['min']
    norm = 1 / np.linalg.norm(diag)
    centre = stats['centroid']

    vertices = input_mesh.vertices
    vNorm = (vertices - centre) * norm
    input_mesh.vertices = vNorm

    return input_mesh


def generate_image_mesh_dictionary(base_path = '/home/qilin/3DGEN/Beam-dataset-generation', mesh_subdir='./deformed_beam',
                                   image_subdir='./imgs', output_filename='mesh_img_dictionary.json', file_type = '.obj'):
    """
    Generate a dictionary mapping meshes to their corresponding images and write to a JSON file.

    Args:
    - base_path (str): The absolute path to the parent directory.
    - mesh_subdir (str): The subdirectory containing mesh files.
    - image_subdir (str): The subdirectory containing image directories corresponding to meshes.
    - output_filename (str): Name of the output JSON file.

    Returns:
    None
    """

    # Define directories
    mesh_dir = os.path.join(base_path, mesh_subdir)
    image_base_dir = os.path.join(base_path, image_subdir)

    # Initialize the dictionary
    mesh_to_images = {}

    # Traverse the mesh directory
    for mesh_file in os.listdir(mesh_dir):
        if mesh_file.endswith(file_type):
            # Remove .obj extension to get the mesh name
            mesh_name = os.path.splitext(mesh_file)[0]

            # Corresponding image directory
            image_dir = os.path.join(image_base_dir, mesh_name)

            if os.path.exists(image_dir):  # Ensure the image directory exists
                # List all images in the directory with their absolute paths
                images = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if
                          img.endswith(('.png', '.jpg'))]  # Assumes images are PNG or JPG. Modify as needed.

                # Update the dictionary
                mesh_to_images[mesh_name] = images

    # Write the dictionary to a JSON file
    with open(output_filename, 'w') as outfile:
        json.dump(mesh_to_images, outfile, indent=4)

    print("JSON file created successfully!")












