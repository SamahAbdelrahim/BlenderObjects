import trimesh
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

_ROOT = Path(__file__).resolve().parents[2]
# Test with a single STL file
stl_path = str(_ROOT / "data" / "abstract-25" / "stl" / "2" / "2-45-B2.stl")
output_path = str(_ROOT / "archive" / "scratch" / "test_matplotlib_output.png")

print(f"Testing matplotlib approach with: {stl_path}")

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

# Create figure and 3D axis
fig = plt.figure(figsize=(5.12, 5.12), dpi=100)
ax = fig.add_subplot(111, projection='3d')

# Get vertices and faces
vertices = mesh.vertices
faces = mesh.faces

# Create polygons for each face
polygons = []
for face in faces:
    polygon = [vertices[vertex] for vertex in face]
    polygons.append(polygon)

# Create Poly3DCollection
poly3d = Poly3DCollection(polygons, alpha=0.8, facecolor='lightgray', 
                         edgecolor='black', linewidth=0.5)
ax.add_collection3d(poly3d)

# Set view limits and camera position
bounds = mesh.bounds
center = (bounds[0] + bounds[1]) / 2
max_range = np.max(bounds[1] - bounds[0]) / 2

ax.set_xlim(center[0] - max_range, center[0] + max_range)
ax.set_ylim(center[1] - max_range, center[1] + max_range)
ax.set_zlim(center[2] - max_range, center[2] + max_range)

# Set camera position
ax.view_init(elev=20, azim=45)

# Set background color
ax.set_facecolor([0.1, 0.3, 0.8])
fig.patch.set_facecolor([0.1, 0.3, 0.8])

# Remove axes
ax.set_axis_off()

# Adjust layout and save
plt.tight_layout()
plt.savefig(output_path, dpi=100, bbox_inches='tight', 
            facecolor=[0.1, 0.3, 0.8], edgecolor='none')
plt.close()

print(f"✅ Test render saved to: {output_path}") 