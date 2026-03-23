import trimesh
import pyvista as pv
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cv2
from PIL import Image
import tempfile

_ROOT = Path(__file__).resolve().parents[2]
_AB25 = _ROOT / "data" / "abstract-25"

### === CONFIGURATION === ###
input_folder = str(_AB25 / "stl")
output_folder = str(_AB25 / "animations")
frames = 120  # total frames in animation (e.g., 120 frames for 4s at 30fps)
fps = 30
resolution = (512, 512)
rotation_axis = 'Z'  # rotate around Z axis
animation_length_seconds = 4
degrees_to_rotate = 360  # full rotation

def center_and_scale_mesh(mesh, target_size=2.0):
    """Center and scale mesh to consistent size"""
    # Get the bounding box
    bounds = mesh.bounds
    min_coords = bounds[0]
    max_coords = bounds[1]
    
    # Calculate center and dimensions
    center = (min_coords + max_coords) / 2
    dimensions = max_coords - min_coords
    max_dim = np.max(dimensions)
    
    # Center the mesh
    mesh.vertices -= center
    
    # Scale to target size
    if max_dim > 0:
        scale_factor = target_size / max_dim
        mesh.vertices *= scale_factor
    
    return target_size

def create_rotation_matrix(angle_degrees, axis='Z'):
    """Create rotation matrix for given angle and axis"""
    angle_rad = np.radians(angle_degrees)
    
    if axis == 'X':
        return np.array([
            [1, 0, 0],
            [0, np.cos(angle_rad), -np.sin(angle_rad)],
            [0, np.sin(angle_rad), np.cos(angle_rad)]
        ])
    elif axis == 'Y':
        return np.array([
            [np.cos(angle_rad), 0, np.sin(angle_rad)],
            [0, 1, 0],
            [-np.sin(angle_rad), 0, np.cos(angle_rad)]
        ])
    else:  # Z axis
        return np.array([
            [np.cos(angle_rad), -np.sin(angle_rad), 0],
            [np.sin(angle_rad), np.cos(angle_rad), 0],
            [0, 0, 1]
        ])

def render_frame(mesh, angle_degrees, output_path, object_size=2.0):
    """Render a single frame of the rotating object"""
    # Create a copy of the mesh for this frame
    frame_mesh = mesh.copy()
    
    # Apply rotation
    rotation_matrix = create_rotation_matrix(angle_degrees, rotation_axis)
    frame_mesh.vertices = frame_mesh.vertices @ rotation_matrix.T
    
    # Convert to PyVista mesh for rendering
    pv_mesh = pv.wrap(frame_mesh)
    
    # Create a plotter
    plotter = pv.Plotter(off_screen=True, window_size=resolution)
    
    # Set up camera position (similar to the Blender script)
    distance = object_size * 3.0
    camera_position = (distance * 0.8, -distance * 0.8, object_size * 0.2)
    plotter.camera_position = [camera_position, (0, 0, 0), (0, 0, 1)]
    
    # Add the mesh with material
    plotter.add_mesh(pv_mesh, color='lightgray', metallic=0.0, roughness=0.6, 
                    specular=1.0, specular_power=10)
    
    # Set background color (deep blue like in the Blender script)
    plotter.set_background([0.1, 0.3, 0.8])
    
    # Render the frame
    plotter.screenshot(output_path)
    plotter.close()

def create_animation(stl_path, output_path, object_size=2.0):
    """Create animation from STL file"""
    print(f"Processing {stl_path}")
    
    # Load the STL file
    mesh = trimesh.load(stl_path)
    
    # Center and scale the mesh
    object_size = center_and_scale_mesh(mesh, target_size=object_size)
    
    # Create temporary directory for frames
    with tempfile.TemporaryDirectory() as temp_dir:
        frame_paths = []
        
        # Generate frames
        for frame in range(frames):
            angle = (frame / frames) * degrees_to_rotate
            frame_path = os.path.join(temp_dir, f"frame_{frame:04d}.png")
            render_frame(mesh, angle, frame_path, object_size)
            frame_paths.append(frame_path)
        
        # Combine frames into video using OpenCV
        if frame_paths:
            # Read first frame to get dimensions
            first_frame = cv2.imread(frame_paths[0])
            height, width, layers = first_frame.shape
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Add frames to video
            for frame_path in frame_paths:
                frame = cv2.imread(frame_path)
                video_writer.write(frame)
            
            video_writer.release()
            print(f"✅ Rendered: {output_path}")

def main():
    """Main function to process all STL files"""
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Recursively process all STL files in subfolders
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith(".stl"):
                stl_path = os.path.join(root, filename)
                
                # Compute relative path from input_folder
                rel_dir = os.path.relpath(root, input_folder)
                
                # Mirror the subfolder structure in output_folder
                output_subfolder = os.path.join(output_folder, rel_dir)
                os.makedirs(output_subfolder, exist_ok=True)
                
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_subfolder, base_name + ".mp4")
                
                # Create animation
                create_animation(stl_path, output_path)
    
    print("✅ All STL files processed.")

if __name__ == "__main__":
    main() 