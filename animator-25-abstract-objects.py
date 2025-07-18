import bpy
import os
from math import radians
import bmesh
from mathutils import Vector

# Enable the STL import/export add-on
import addon_utils
addon_utils.enable("io_mesh_stl")

### === CONFIGURATION === ###
input_folder = "./25-abstract-stl"
output_folder = "./25-abstract-animations"
frames = 120  # total frames in animation (e.g., 120 frames for 4s at 30fps)
fps = 30
resolution = (512, 512)
rotation_axis = 'Z'  # rotate around Z axis
animation_length_seconds = 4
degrees_to_rotate = 360  # full rotation
output_format = "MPEG4"
video_codec = "H264"
file_format = "FFMPEG"

### === SET RENDER SETTINGS === ###
bpy.context.scene.render.image_settings.file_format = file_format
bpy.context.scene.render.fps = fps
bpy.context.scene.render.resolution_x = resolution[0]
bpy.context.scene.render.resolution_y = resolution[1]
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.ffmpeg.format = output_format
bpy.context.scene.render.ffmpeg.codec = video_codec
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'

# Set render engine to Cycles for better quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32  # Lower samples for faster testing
bpy.context.scene.cycles.use_denoising = True  # Enable denoising for cleaner results

# Increase exposure for brighter rendering
bpy.context.scene.view_settings.exposure = 1.0  # Increase exposure

### === UTILITY FUNCTIONS === ###

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)

def get_object_bounds(obj):
    """Get the actual bounding box of the object in world space"""
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(corner.x for corner in bbox_corners)
    max_x = max(corner.x for corner in bbox_corners)
    min_y = min(corner.y for corner in bbox_corners)
    max_y = max(corner.y for corner in bbox_corners)
    min_z = min(corner.z for corner in bbox_corners)
    max_z = max(corner.z for corner in bbox_corners)
    
    center = Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
    size = Vector((max_x - min_x, max_y - min_y, max_z - min_z))
    return center, size

def setup_scene(obj):
    # Center the object properly
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    
    # Get object bounds for camera positioning
    center, size = get_object_bounds(obj)
    max_dim = max(size.x, size.y, size.z)
    
    # Add camera with better positioning
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    
    # Position camera at eye level (like holding the object)
    distance = max_dim * 3.5  # Increase distance to capture full object
    cam.location = (distance * 0.8, -distance * 0.8, size.z * 0.3)  # Slightly above center
    
    # Point camera at the center of the object
    direction = center - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # Camera settings for better framing
    cam.data.lens = 50  # Standard lens
    cam.data.clip_end = 1000
    
    # Setup improved lighting for even illumination
    setup_lighting(max_dim)
    
    # Setup world background
    setup_world_background()
    
    # Apply material to object
    apply_material(obj)

def setup_lighting(max_dim):
    """Setup very bright, direct lighting for clear visibility"""
    distance = max_dim * 3
    
    # Main light - extremely bright
    main_light_data = bpy.data.lights.new(name="MainLight", type='SUN')
    main_light_data.energy = 10  # Much brighter
    main_light = bpy.data.objects.new(name="MainLight", object_data=main_light_data)
    bpy.context.collection.objects.link(main_light)
    main_light.location = (distance, -distance, distance)
    main_light.rotation_euler = (radians(45), 0, radians(45))
    
    # Fill light - also very bright
    fill_light_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_light_data.energy = 8
    fill_light = bpy.data.objects.new(name="FillLight", object_data=fill_light_data)
    bpy.context.collection.objects.link(fill_light)
    fill_light.location = (-distance, distance, distance * 0.5)
    fill_light.rotation_euler = (radians(30), 0, radians(-135))
    
    # Top light - bright overhead
    top_light_data = bpy.data.lights.new(name="TopLight", type='SUN')
    top_light_data.energy = 6
    top_light = bpy.data.objects.new(name="TopLight", object_data=top_light_data)
    bpy.context.collection.objects.link(top_light)
    top_light.location = (0, 0, distance * 2)
    top_light.rotation_euler = (0, 0, 0)
    
    # Front light for direct illumination
    front_light_data = bpy.data.lights.new(name="FrontLight", type='SUN')
    front_light_data.energy = 5
    front_light = bpy.data.objects.new(name="FrontLight", object_data=front_light_data)
    bpy.context.collection.objects.link(front_light)
    front_light.location = (0, -distance, 0)
    front_light.rotation_euler = (radians(90), 0, 0)

def setup_world_background():
    """Setup pure white world background for high contrast"""
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    
    # Add background node with pure white background
    bg_node = nodes.new(type='ShaderNodeBackground')
    #bg_node.inputs[0].default_value = (0.4, 0.7, 1.0, 1)  # Light sky blue
    bg_node.inputs[0].default_value = (0.1, 0.3, 0.8, 1)  # deeper blue

    bg_node.inputs[1].default_value = 1.0  # Normal strength
    
    # Add world output
    output_node = nodes.new(type='ShaderNodeOutputWorld')
    world.node_tree.links.new(bg_node.outputs[0], output_node.inputs[0])

def apply_material(obj):
    """Apply a medium gray, matte material for good contrast"""
    mat = bpy.data.materials.new(name="ObjectMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Add Principled BSDF with medium gray
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.25, 0.25, 0.25, 1.0)  # Dark gray
    principled.inputs['Metallic'].default_value = 0.0  # No metallic
    principled.inputs['Roughness'].default_value = 0.8  # Very rough/matte
    
    # Handle different Blender versions for specular input
    try:
        principled.inputs['Specular IOR Level'].default_value = 1.0
    except KeyError:
        try:
            principled.inputs['Specular'].default_value = 1.0
        except KeyError:
            pass
    
    # Add material output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    links.new(principled.outputs[0], output.inputs[0])
    
    # Apply material to object
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def animate_rotation(obj, total_frames):
    """Animate object rotation"""
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    
    if rotation_axis == 'X':
        obj.rotation_euler = (radians(degrees_to_rotate), 0, 0)
    elif rotation_axis == 'Y':
        obj.rotation_euler = (0, radians(degrees_to_rotate), 0)
    else:  # Z axis
        obj.rotation_euler = (0, 0, radians(degrees_to_rotate))
    
    obj.keyframe_insert(data_path="rotation_euler", frame=total_frames)
    
    # Set interpolation to linear for smooth rotation
    if obj.animation_data:
        for fcurve in obj.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'

def render_video(output_path):
    """Render the animation"""
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(animation=True)

### === MAIN SCRIPT === ###

# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".stl"):
        print(f"Processing {filename}")
        clear_scene()
        
        # Import STL file
        stl_path = os.path.join(input_folder, filename)
        bpy.ops.import_mesh.stl(filepath=stl_path)
        obj = bpy.context.selected_objects[0]
        
        # Setup scene, lighting, and camera
        setup_scene(obj)
        
        # Animate rotation
        animate_rotation(obj, frames)
        
        # Render video
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, base_name + ".mp4")
        render_video(output_path)
        
        print(f"✅ Rendered: {output_path}")

print("✅ All STL files processed.")