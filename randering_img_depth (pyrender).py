import numpy as np
import trimesh
import pyrender
import imageio
import os
from PIL import Image as Img
import random
import json
import re
import cv2

# Define the function to create rotation matrix from roll, pitch, and yaw
def rotation_matrix(roll, pitch, yaw):
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])
    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])
    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])
    R = np.dot(R_z, np.dot(R_y, R_x))
    return R


deformed_mesh_meta_path = "./cantilevers/deformed_info.json"
with open(deformed_mesh_meta_path) as meta:
    # Read the file contents
    json_data = meta.read()

    # Parse the JSON data
    data = json.loads(json_data)
    paths = []  # List to store path values
    for key in data.keys():
        # Check if the key starts with 'b'
        if key.startswith('b'):
            # Access the value associated with the target key
            target_value = data[key]

            # Check if '25' and '50' keys exist
            if '100' in target_value:
            # Access the values inside '25' and '50' keys
                value_100 = target_value['100']


            # Iterate over the random number keys inside '25'
            for inner_key_100 in value_100.keys():
                # Check if the inner key is a random number
                if inner_key_100.isdigit():
                    # Access the 'path' value inside the random number key
                    path_value = value_100[inner_key_100].get('Path')
                    if path_value:
                        paths.append(path_value)


dir_1 = "./cantilever_images"
json_path = "{}/img_info.json".format(dir_1)
os.makedirs(dir_1, exist_ok=True)
renderer = pyrender.OffscreenRenderer(896, 896)
for path in paths:
    pattern = r"beam_(\d+)/deformed_(\d+)/deformed_\d+_(\d+)\.obj"
    matches = re.search(pattern, path)
    mesh_name = "beam_" + matches.group(1) + "_" + matches.group(2) + "_" + matches.group(3)
    dir_2 = "./cantilever_images"
    #os.makedirs(dir_2, exist_ok=True)
    mesh = trimesh.load_mesh(path)
    mesh = pyrender.Mesh.from_trimesh(mesh)

    # Create a scene
    scene = pyrender.Scene()
    # Add the mesh to the scene
    scene.add(mesh)
    # Create a light source
    directional_light_color = np.array([1.0, 0.90, 0.7])
    directional_light_intensity = 1.5
    light = pyrender.DirectionalLight(color=directional_light_color, intensity=directional_light_intensity)
    # Create a camera
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)

    # Get the center of the mesh
    bounds = mesh.bounds
    center = bounds.mean(axis=0)
    print(center)
    size = bounds[1] - bounds[0]
    # Define the distance of the camera from the center of the mesh
    distance = np.max(size) + center[2]
    img_info = {}
    img_path_info = {}
    mesh_path_info = {}
    # random generate camera_pose based on the yaw and pitch
    for k in range(30):
        yaw = random.uniform(0, 2 * np.pi)  # random yaw angle
        pitch = random.uniform(0, np.pi)  # random pitch angle
        roll = 0  # you can change this as needed
        eye = center + distance * np.array([np.sin(pitch) * np.cos(yaw), np.sin(pitch) * np.sin(yaw), np.cos(pitch)])
        R = rotation_matrix(roll, pitch, yaw)
        camera_pose = np.eye(4)
        camera_pose[:3, :3] = R
        camera_pose[:3, 3] = eye

        # Add the camera and light to the scene
        camera_node = scene.add(camera, pose=camera_pose)
        light_node = scene.add(light, pose=camera_pose)

        # Render the scene
        color, depth = renderer.render(scene)
        image = Img.fromarray((color * 255).astype(np.uint8))
        depth_map = cv2.normalize(depth, None, 255, 0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        #print(np.unique(depth))

        # Remove the camera and light from the scene
        scene.remove_node(camera_node)
        scene.remove_node(light_node)
        # Save the image
        img_path = "{}/{}_{}_image.png".format(dir_2, mesh_name, k)
        depth_path = "{}/{}_{}_depth.png".format(dir_2, mesh_name, k)
        print(img_path, depth_path)
        imageio.imsave(img_path, image)
        imageio.imsave(depth_path, depth_map)


