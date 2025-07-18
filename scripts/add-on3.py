import bpy
import os
import math
import random
import time

# Set up output path
#output_path = "/Users/samahabdelrahim/Desktop/blender_videos/"
output_path= "/Users/samahabdelrahim/git-repos/BlenderObjects/blender_videos/"
os.makedirs(output_path, exist_ok=True)

def create_object_with_complexity(complexity_level):
    print(f"Creating object with complexity level {complexity_level}")
    
    before = set(bpy.data.objects)
    
    # Generate shape with varying parameters
    bpy.ops.mesh.shape_generator(
        random_seed=random.randint(0, 10000),
        min_extrude=0.1,
        max_extrude=0.3 + 0.2 * complexity_level,
        min_rotation=0,
        max_rotation=360,
        number_to_create=1,
        auto_update=True
    )
    
    bpy.ops.mesh.shape_generator_bake()
    time.sleep(0.1)
    
    after = set(bpy.data.objects)
    new_objs = list(after - before)
    
    obj = next((o for o in new_objs if o.type == 'MESH'), None)
    if obj is None:
        raise RuntimeError("No mesh object found after shape generation.")
    
    # Move object to origin and adjust scale
    obj.location = (0, 0, 0)  # Center the object
    obj.scale = (2, 2, 2)     # Make it larger
    
    obj.name = f"stimulus_{complexity_level}"
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    return obj

def setup_scene():
    # Clear EVERYTHING first
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create fresh camera with better positioning
    bpy.ops.object.camera_add(location=(0, -8, 4))  # Moved further back and higher
    camera = bpy.context.active_object
    camera.name = "OrbitCamera"
    camera.rotation_euler = (math.radians(25), 0, 0)  # Adjusted angle
    
    # Add lighting with adjusted positioning for better illumination
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun_obj = bpy.context.active_object
    sun_obj.data.energy = 10.0  # Increased light intensity
    
    # Add a second light for better illumination
    bpy.ops.object.light_add(type='POINT', location=(-5, 5, 5))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 1000.0
    
    return camera

def create_orbit_path(camera, target):
    # Create orbit path with adjusted parameters
    bpy.ops.curve.primitive_bezier_circle_add(radius=8, location=(0, 0, 4))  # Higher position
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
    
    # Offset the path slightly
    path.rotation_euler.x = math.radians(15)  # Tilt the orbit path
    
    return path


def main():
    num_shapes = 2
    
    for i in range(num_shapes):
        # Create fresh scene with new camera for each iteration
        camera = setup_scene()
        
        # Create object with complexity level
        obj = create_object_with_complexity(i)
        
        # Setup orbit path around the object
        create_orbit_path(camera, obj)
        
        # Set as active camera
        bpy.context.scene.camera = camera
        
        # Render the animation
        render_animation(f"shape_generator_object_{i+1}")
        
        print(f"Completed object {i+1}/{num_shapes}")

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


if __name__ == "__main__":
    main()