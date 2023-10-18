import numpy as np
import trimesh
import pyrender
import imageio
import os
import random
import cv2  # For depth map normalization


def rotation_matrix(roll, pitch, yaw):
    """
    Generate a 3D rotation matrix based on roll, pitch, and yaw angles.

    Args:
    - roll (float): Rotation around the x-axis.
    - pitch (float): Rotation around the y-axis.
    - yaw (float): Rotation around the z-axis.

    Returns:
    - numpy.array: A 3x3 rotation matrix.
    """

    # Define rotation matrices for each axis
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])
    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])
    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])

    # Combine rotations
    return np.dot(R_z, np.dot(R_y, R_x))


def generate_cantilever_images(input_dir="./deformed_beam",
                               output_dir="./imgs",
                               num_images = 1,
                               img_size=(1792, 1792),
                               yfov=np.pi/2,
                               roll=0,
                               yaw=(-2* np.pi, 2* np.pi),
                               pitch=(-np.pi / 2, np.pi / 2),
                               light_intensity = 1.5,
                               light_color=np.array([1.0, 0.90, 0.7])):
    """
    Generates rendered images and depth maps from beam meshes in a directory.

    Args:
    - input_dir (str): Directory containing the mesh files (.obj).
    - output_dir (str): Directory to save the rendered images and depth maps.
    - num_images (int): Number of images to generate for each mesh.
    - img_size (tuple): Size of the rendered images.
    - yfov (float): Field of view for the camera.
    - roll (float or tuple): Roll angle(s) for the camera.
    - yaw (float or tuple): Yaw angle(s) for the camera.
    - pitch (float or tuple): Pitch angle(s) for the camera.
    - light_color (numpy.array): RGB color for the light source.
    """

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize the renderer with the desired image size
    renderer = pyrender.OffscreenRenderer(*img_size)

    # Extract paths of all .obj files in the input directory
    paths = [os.path.join(input_dir, fname) for fname in os.listdir(input_dir) if fname.endswith('.obj')]

    # Iterate over each mesh
    for path in paths:
        # Create a directory specific to the current mesh to store its images
        mesh_subdir = os.path.join(output_dir, os.path.splitext(os.path.basename(path))[0])
        os.makedirs(mesh_subdir, exist_ok=True)

        # Load the mesh and convert it to a format suitable for rendering
        mesh = trimesh.load_mesh(path)
        mesh = pyrender.Mesh.from_trimesh(mesh)

        # Create a scene and add the mesh
        scene = pyrender.Scene()
        scene.add(mesh)

        # Configure light source
        light = pyrender.DirectionalLight(color=light_color, intensity=light_intensity)
        # Configure camera
        camera = pyrender.PerspectiveCamera(yfov=yfov)

        # Compute the center of the mesh
        bounds = mesh.bounds
        center = bounds.mean(axis=0)

        # Compute the diagonal of the bounding box
        diagonal = np.linalg.norm(bounds[1] - bounds[0])
        half_diagonal = diagonal

        # Calculate the distance based on the diagonal and the FOV.
        # The formula is derived from the tangent half-angle formula: tan(fov/2) = (half_diagonal / distance)
        distance = half_diagonal / np.tan(yfov/2)

        # Render images from different viewpoints
        for k in range(num_images):
            current_yaw = random.uniform(*yaw) if isinstance(yaw, tuple) else yaw
            current_pitch = random.uniform(*pitch) if isinstance(pitch, tuple) else pitch
            current_roll = random.uniform(*roll) if isinstance(roll, tuple) else roll

            # Compute the camera position and orientation
            eye = center + distance * np.array([np.sin(current_pitch) * np.cos(current_yaw),
                                                np.sin(current_pitch) * np.sin(current_yaw),
                                                np.cos(current_pitch)])
            # Compute the camera orientation to always look at the center
            R = rotation_matrix(current_roll, current_pitch, current_yaw)
            camera_pose = np.eye(4)
            camera_pose[:3, :3] = R
            camera_pose[:3, 3] = eye

            # Add camera and light to the scene
            camera_node = scene.add(camera, pose=camera_pose)
            light_node = scene.add(light, pose=camera_pose)

            # Render the scene capturing both color and depth information
            color, depth = renderer.render(scene)

            # Normalize the depth map for visualization
            depth_map = cv2.normalize(depth, None, 255, 0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Save the color image and depth map
            img_path = os.path.join(mesh_subdir, "image_{:04}.png".format(k))
            depth_path = os.path.join(mesh_subdir, "depth_{:04}.png".format(k))
            imageio.imsave(img_path, (color * 255).astype(np.uint8))
            imageio.imsave(depth_path, depth_map)

            # Remove camera and light from the scene to reset for next render
            scene.remove_node(camera_node)
            scene.remove_node(light_node)


# Example usage:
generate_cantilever_images()
