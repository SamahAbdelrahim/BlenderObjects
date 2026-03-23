import trimesh
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cv2
import tempfile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

_ROOT = Path(__file__).resolve().parents[2]
# Test configuration
stl_path = str(_ROOT / "data" / "abstract-25" / "stl" / "2" / "2-45-B2.stl")
output_path = str(_ROOT / "archive" / "scratch" / "test_animation.mp4")
frames = 30  # Reduced for testing
fps = 10
resolution = (512, 512)
rotation_axis = 'Z'
degrees_to_rotate = 360

def center_and_scale_mesh(mesh, target_size=2.0):
    """Center and scale mesh to consistent size"""
    bounds = mesh.bounds
    min_coords = bounds[0]
    max_coords = bounds[1]
    center = (min_coords + max_coords) / 2
    dimensions = max_coords - min_coords
    max_dim = np.max(dimensions)
    
    mesh.vertices -= center
    if max_dim > 0:
        scale_factor = target_size / max_dim
        mesh.vertices *= scale_factor
    
    return target_size

def create_rotation_matrix(angle_degrees, axis='Z'):
    """Create rotation matrix for given angle and axis"""
    angle_rad = np.radians(angle_degrees)
    
    if axis == 'Z':
        return np.array([
            [np.cos(angle_rad), -np.sin(angle_rad), 0],
            [np.sin(angle_rad), np.cos(angle_rad), 0],
            [0, 0, 1]
        ])
    return np.eye(3)

def render_frame_matplotlib(mesh, angle_degrees, output_path, object_size=2.0):
    """Render a single frame using matplotlib"""
    frame_mesh = mesh.copy()
    
    # Apply rotation
    rotation_matrix = create_rotation_matrix(angle_degrees, rotation_axis)
    frame_mesh.vertices = frame_mesh.vertices @ rotation_matrix.T
    
    # Create figure and 3D axis
    fig = plt.figure(figsize=(resolution[0]/100, resolution[1]/100), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    
    # Get vertices and faces
    vertices = frame_mesh.vertices
    faces = frame_mesh.faces
    
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
    bounds = frame_mesh.bounds
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

def create_test_animation(stl_path, output_path, object_size=2.0):
    """Create test animation from STL file"""
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
            render_frame_matplotlib(mesh, angle, frame_path, object_size)
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
            print(f"✅ Test animation saved to: {output_path}")

# Run the test
create_test_animation(stl_path, output_path) 