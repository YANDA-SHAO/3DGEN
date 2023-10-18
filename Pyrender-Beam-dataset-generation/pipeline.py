from utils import *
from base_beam_generator import *
from deformed_beam_generator import *
from randering_img_depth import *

# Step 1: Generate base beam meshes.
generate_beam_meshes(
    output_dir="./base_beams",
    split=4,
    num_heights=2,
    num_widths=2,
    start_height=0.02,
    end_height=0.05,
    min_width_ratio=1,
    max_width_ratio=2
)

# Step 2: Deform the generated beam meshes.
generate_deformed_meshes(
    beam_type='cantilever',
    mesh_meta_path="./base_beams/mesh_meta.xlsx",
    output_dir="./deformed_beam",
    num_meshes=5,
    youngs_modulus=69000000000,
    max_displacement=-0.03,
    min_displacement=0.03,
    locations=[0.9, 0.1]
)

# Step 3: Render the deformed beam meshes.
generate_cantilever_images(
    input_dir="./deformed_beam",
    output_dir="./rendered_images",
    num_images=1,
    img_size=(1792, 1792),
    yfov=np.pi / 3.0,
    roll=0,
    yaw=(-2 * np.pi, 2* np.pi),
    pitch=(-np.pi / 2, np.pi / 2),
    light_color=np.array([1.0, 0.90, 0.7])
)

generate_image_mesh_dictionary()
