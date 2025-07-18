import bpy
import os
import math
import random
import time
import json

# Enable STL exporter add-on
bpy.ops.preferences.addon_enable(module="io_mesh_stl")


# Set up output path for STL files
output_path = "/Users/samahabdelrahim/git-repos/BlenderObjects/stl_files/"
os.makedirs(output_path, exist_ok=True)

def create_object_with_complexity(complexity_level):
    print(f"Creating object with complexity level {complexity_level}")
    
    before = set(bpy.data.objects)
    
    # Store parameters for this object
    random_seed = random.randint(0, 10000)
    max_extrude_val = 0.3 + 0.2 * complexity_level
    
    parameters = {
        "complexity_level": complexity_level,
        "random_seed": random_seed,
        "min_extrude": 0.1,
        "max_extrude": max_extrude_val,
        "min_rotation": 0,
        "max_rotation": 360,
        "scale": [2, 2, 2],
        "location": [0, 0, 0]
    }
    
    # Generate shape with varying parameters
    bpy.ops.mesh.shape_generator(
        random_seed=random_seed,
        min_extrude=parameters["min_extrude"],
        max_extrude=parameters["max_extrude"],
        min_rotation=parameters["min_rotation"],
        max_rotation=parameters["max_rotation"],
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
    
    # Store parameters in a JSON file
    params_path = os.path.join(output_path, f"shape_generator_object_{complexity_level+1}_params.json")
    with open(params_path, 'w') as f:
        json.dump(parameters, f, indent=4)
    print(f"Saved parameters to: {params_path}")
    
    return obj

def save_object_as_stl(obj, filename):
    # Ensure the STL exporter is available
    bpy.ops.preferences.addon_enable(module="io_mesh_stl")

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    stl_path = os.path.join(output_path, f"{filename}.stl")

    bpy.ops.export_mesh.stl(
        filepath=stl_path,
        use_selection=True
    )
    print(f"Saved STL file: {stl_path}")



def main():
    num_shapes = 2
    
    for i in range(num_shapes):
        # Clear previous objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Create object with complexity level
        obj = create_object_with_complexity(i)
        
        # Save as STL
        save_object_as_stl(obj, f"shape_generator_object_{i+1}")
        
        print(f"Completed object {i+1}/{num_shapes}")

if __name__ == "__main__":
    main()