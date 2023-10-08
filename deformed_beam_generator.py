# This code is for generate deformed simple support beam meshes.
from analytic_functions import cantilever, cantilever_power_estimation, simple_support_beam, simple_support_beam_power_estimation
import pandas as pd
import trimesh
import os
import json
import numpy as np

mesh_meta_path = "./base_beams/mesh_meta.xlsx"
mesh_meta = pd.read_excel(mesh_meta_path)
os.makedirs("beam_SM_beam", exist_ok=True)
deformed_info = {}
k = 0
i = 0
for _, example in mesh_meta.iterrows():
    # calculation of the modulus of elasticity. example[3]: height, example[4]: width
    I = example.Height*(example.Width**3)/12
    # Young's modulus for steel
    E = 69000000000
    Location = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    num_mesh = 10
    dir = "./beam_SM_beam"
    os.makedirs(dir, exist_ok=True)
    location_info = {}
    for loc in Location:
        k = k + 1
        #loc_dir = "{}/deformed_{}".format(dir, int(loc*100))
        #os.makedirs(loc_dir, exist_ok=True)
        Dpower_max = simple_support_beam_power_estimation(1, -0.03, E, I, loc)
        Dpower_min = simple_support_beam_power_estimation(1, 0.03, E, I, loc)
        Dpowers = np.linspace(Dpower_min, Dpower_max, num_mesh)
        print(len(Dpowers))
        power_info = {}
        for power in Dpowers:
            i = i + 1
            beam = trimesh.load_mesh(example.Path)
            deformed_beam = simple_support_beam(beam, power, loc, E, I)
            deformed_mesh_path = "{}/SM_beam{}_{}.obj".format(dir, k, i)
            deformed_beam.export(deformed_mesh_path, file_type="obj")

            deformed_beam_info = {
                "Path": deformed_mesh_path,
                "E": E,
                "I": I,
            }
            power_info[abs(power)] = deformed_beam_info

        # Add the power_info dictionary to the location_info dictionary using the location as the key
        location_info[int(loc*100)] = power_info

        # Add the location_info dictionary to the deformed_info dictionary using the beam name as the key
    deformed_info[example.Name] = location_info
json_path = "./deformed_info.json"
with open(json_path, "w") as json_file:
    json.dump(deformed_info, json_file)
print("Deformed beam information saved as JSON file:", json_path)



