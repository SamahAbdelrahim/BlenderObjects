import bpy
import os
import math
import random
import time
import json

# Enable STL exporter add-on
bpy.ops.preferences.addon_enable(module="io_mesh_stl")


# Set up output path for STL files
output_path = "/Users/samahabdelrahim/git-repos/BlenderObjects/stl_parameters/"
os.makedirs(output_path, exist_ok=True)

def create_object_with_complexity(complexity_level, num_extrusions=None, extrusion_range=None, rotation_range=None, random_seed=None):
    print(f"Creating object with complexity level {complexity_level}")
    
    before = set(bpy.data.objects)
    
    # Use provided parameters or generate defaults
    random_seed = random_seed if random_seed is not None else random.randint(0, 10000)
    min_extrude = 0.1
    max_extrude = min_extrude + (extrusion_range if extrusion_range is not None else 0.2)
    max_rotation = rotation_range if rotation_range is not None else 360
    
    parameters = {
        "complexity_level": complexity_level,
        "random_seed": random_seed,
        "num_extrusions": num_extrusions,
        "min_extrude": min_extrude,
        "max_extrude": max_extrude,
        "extrusion_range": max_extrude - min_extrude,
        "min_rotation": 0,
        "max_rotation": max_rotation,
        "rotation_range": max_rotation,
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
        number_to_create=num_extrusions if num_extrusions is not None else 1,
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
    # Parameter grid for systematic exploration with more balanced ranges
    num_extrusions_range = [1, 2, 3, 4, 5, 6, 8, 10]  # Added more simple options
    extrusion_ranges = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4]  # Added finer control at lower ranges
    rotation_ranges = [30, 45, 90, 180, 360]  # Added smaller rotation option
    random_seeds = [random.randint(0, 10000) for _ in range(3)]  # Reduced to 3 seeds to manage total combinations
    
    # Calculate total combinations
    total_combinations = len(num_extrusions_range) * len(extrusion_ranges) * len(rotation_ranges) * len(random_seeds)
    current_combination = 0
    
    # Iterate through parameter combinations
    for num_ext in num_extrusions_range:
        for ext_range in extrusion_ranges:
            # Adjust rotation range based on complexity
            # Simple objects (low extrusions) get more restricted rotation ranges
            available_rotations = rotation_ranges[:2] if num_ext <= 2 else \
                                rotation_ranges[:3] if num_ext <= 4 else \
                                rotation_ranges
            
            for rot_range in available_rotations:
                for seed in random_seeds:
                    # Clear previous objects
                    bpy.ops.object.select_all(action='SELECT')
                    bpy.ops.object.delete()
                    
                    # Create object with specific parameters
                    obj = create_object_with_complexity(
                        complexity_level=current_combination,
                        num_extrusions=num_ext,
                        extrusion_range=ext_range,
                        rotation_range=rot_range,
                        random_seed=seed
                    )
                    
                    # Save as STL
                    filename = f"shape_gen_ext{num_ext}_extrange{ext_range}_rot{rot_range}_seed{seed}"
                    save_object_as_stl(obj, filename)
                    
                    current_combination += 1
                    print(f"Completed combination {current_combination}/{total_combinations}")

if __name__ == "__main__":
    main()