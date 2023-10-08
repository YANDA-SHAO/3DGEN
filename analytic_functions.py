import trimesh
import numpy as np

#####################Creating textured meshes from Trimesh#################
def beam_generator(shape):
    # Define the shape and position of the bridge
    mesh = trimesh.creation.box(shape)
    position = shape/2
    # Combine the shape and position to create the mesh
    cantilever = trimesh.Trimesh(vertices=mesh.vertices+position,faces=mesh.faces)
    cantilever = cantilever.subdivide()
    cantilever = cantilever.subdivide()
    cantilever = cantilever.subdivide()
    cantilever = cantilever.subdivide()
    cantilever = cantilever.subdivide()


    print('Number of vertices:', cantilever.vertices.shape[0])
    print('Number of faces:', cantilever.faces.shape[0])
    return cantilever


def cantilever(mesh, P, E, I,loc):
    L = loc
    # Function for deflection
    for vertic in mesh.vertices:
        x = vertic[0]
        y = (P * x**2 * (3 * L - x)) / (6 * E * I)
        vertic[1] += y  # Add the deflection to the y-coordinate of the vertex
    return mesh


def cantilever_power_estimation(Len, Ddis, E, I):
    Dpower = int((6 * Len * E * I * Ddis) / (Len**3))
    return Dpower

def simple_support_beam(mesh, P, a, E, I):
    L = 1  # Assuming the length of the beam is along the x-axis
    for vertic in mesh.vertices:
        x = vertic[0]
        if x < a:
            y = (P * (L - a) * x * (L**2 - x**2 - (L - a)**2)) / (6 * L * E * I)
        else:
            y = (P * a * (L - x) * (L**2 - (L - x)**2 - a**2)) / (6 * L * E * I)
        vertic[1] += y  # Add the deflection to the y-coordinate of the vertex
    return mesh

def simple_support_beam_power_estimation(Len, Ddis, E, I, loc):
    Dpower = int((6 * Len * E * I * Ddis) / (loc * (Len - loc) * (Len ** 2 - (Len - loc) ** 2 - loc ** 2)))
    return Dpower





