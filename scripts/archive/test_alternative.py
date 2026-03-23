import trimesh
import pyvista as pv
import numpy as np
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
# Test with a single STL file
stl_path = str(_ROOT / "data" / "abstract-25" / "stl" / "2" / "2-45-B2.stl")
output_path = str(_ROOT / "archive" / "scratch" / "test_output.png")

print(f"Testing with: {stl_path}")

# Load the STL file
mesh = trimesh.load(stl_path)
print(f"Loaded mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")

# Center and scale the mesh
bounds = mesh.bounds
min_coords = bounds[0]
max_coords = bounds[1]
center = (min_coords + max_coords) / 2
dimensions = max_coords - min_coords
max_dim = np.max(dimensions)

print(f"Original bounds: {bounds}")
print(f"Center: {center}")
print(f"Max dimension: {max_dim}")

# Center the mesh
mesh.vertices -= center

# Scale to target size
target_size = 2.0
if max_dim > 0:
    scale_factor = target_size / max_dim
    mesh.vertices *= scale_factor

print(f"Scaled to size: {target_size}")

# Convert to PyVista mesh
pv_mesh = pv.wrap(mesh)

# Create a plotter
plotter = pv.Plotter(off_screen=True, window_size=(512, 512))

# Set up camera position
distance = target_size * 3.0
camera_position = (distance * 0.8, -distance * 0.8, target_size * 0.2)
plotter.camera_position = [camera_position, (0, 0, 0), (0, 0, 1)]

# Add the mesh
plotter.add_mesh(pv_mesh, color='lightgray')

# Set background color
plotter.set_background([0.1, 0.3, 0.8])

# Render the frame
plotter.screenshot(output_path)
plotter.close()

print(f"✅ Test render saved to: {output_path}") 