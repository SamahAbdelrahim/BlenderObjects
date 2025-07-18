import bpy
import os
import math
import random

# Set up output path
output_path = "/Users/samahabdelrahim/Desktop/blender_videos/"
os.makedirs(output_path, exist_ok=True)

def create_object_with_complexity(complexity_level):
    """
    Create an object with varying complexity using basic mesh operations
    complexity_level: integer determining object complexity
    """
    # Start with base mesh (cube)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = f"stimulus_{complexity_level}"
    
    # Add complexity through extrusions and modifications
    for i in range(complexity_level + 1):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_random(ratio=0.3)
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate=({"value": (
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(0.2, 1)
            )})
        )
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add bevel modifier
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.1
    bevel.segments = 3
    
    # Add displacement noise
    noise = obj.modifiers.new(name="Displace", type='DISPLACE')
    texture = bpy.data.textures.new('NoiseTexture', type='NOISE')
    noise.strength = 0.05
    noise.texture = texture
    
    # Add material
    material = bpy.data.materials.new(name=f"Material_{complexity_level}")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.8, 0.8, 1)
    
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
    
    return obj

def setup_scene():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Set up camera with better positioning
    bpy.ops.object.camera_add(location=(-10, -2, 6))
    camera = bpy.context.active_object
    camera.name = "OrbitCamera"
    camera.rotation_euler = (math.radians(45), 0, 0)
    
    # Add lighting with better positioning and energy
    sun = bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun_obj = bpy.context.active_object
    sun_obj.data.energy = 5.0
    
    return camera

def create_orbit_path(camera, target):
    # Create circular path with adjusted position
    bpy.ops.curve.primitive_bezier_circle_add(radius=8, location=(0, 0, 5))
    path = bpy.context.active_object
    path.name = "OrbitPath"
    
    # Set up camera constraints
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    # Set up path following
    bpy.context.view_layer.objects.active = camera
    bpy.ops.object.constraint_add(type='FOLLOW_PATH')
    camera.constraints["Follow Path"].target = path
    camera.constraints["Follow Path"].use_curve_follow = True
    
    return path

def render_animation(output_name):
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 120  # 5 seconds at 24fps
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Set output path for this specific object
    scene.render.filepath = os.path.join(output_path, f"{output_name}.mp4")
    
    # Animate path follow
    camera = bpy.context.scene.camera
    fcu = camera.constraints["Follow Path"].driver_add("offset_factor")
    fcu.driver.type = 'SCRIPTED'
    var = fcu.driver.variables.new()
    var.name = 'frame'
    var.type = 'SINGLE_PROP'
    var.targets[0].id_type = 'SCENE'
    var.targets[0].id = scene
    var.targets[0].data_path = 'frame_current'
    fcu.driver.expression = f"frame / {scene.frame_end}"
    
    # Render
    bpy.ops.render.render(animation=True)

def main():
    # Number of shapes to generate with increasing complexity
    num_shapes = 5
    
    for i in range(num_shapes):
        # Setup fresh scene
        camera = setup_scene()
        
        # Create object with current complexity level
        obj = create_object_with_complexity(i)
        
        # Setup camera path
        create_orbit_path(camera, obj)
        
        # Set active camera
        bpy.context.scene.camera = camera
        
        # Render animation
        render_animation(f"shape_generator_object_{i+1}")
        
        print(f"Completed object {i+1}/{num_shapes}")

if __name__ == "__main__":
    main()
