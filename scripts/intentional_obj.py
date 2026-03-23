import bpy
import os
import math
import random

# Enable STL exporter add-on
bpy.ops.preferences.addon_enable(module="io_mesh_stl")

# Set up output path for STL files
output_path = "/Users/samahabdelrahim/git-repos/BlenderObjects/stl_files/"
os.makedirs(output_path, exist_ok=True)

def create_geometric_base(base_type, size=2.0):
    """Create a base geometric shape"""
    if base_type == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(size=size)
    elif base_type == 'CYLINDER':
        bpy.ops.mesh.primitive_cylinder_add(radius=size/2, depth=size)
    elif base_type == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size/2)
    return bpy.context.active_object

def create_intentional_object(complexity_level):
    """Create an object with intentional, meaningful structure"""
    print(f"Creating intentional object with complexity level {complexity_level}")
    
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Choose base shape based on complexity
    base_types = ['CUBE', 'CYLINDER', 'SPHERE']
    base_type = base_types[complexity_level % len(base_types)]
    
    # Create base object
    obj = create_geometric_base(base_type)
    
    # Enter edit mode for modifications
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Apply intentional modifications based on complexity
    if complexity_level > 0:
        # Create symmetric patterns
        for i in range(min(complexity_level, 4)):
            # Extrude faces with controlled randomness
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={
                    "value": (
                        math.cos(i * math.pi/2) * 0.5,
                        math.sin(i * math.pi/2) * 0.5,
                        0.5
                    )
                }
            )
            # Add geometric detail
            bpy.ops.mesh.bevel(offset=0.1, segments=3)
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Apply modifiers for final touch
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.05
    bevel.segments = 3
    
    # Name and position the object
    obj.name = f"intentional_shape_{complexity_level}"
    obj.location = (0, 0, 0)
    
    return obj

def save_object_as_stl(obj, filename):
    """Save the object as an STL file"""
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
    num_shapes = 5  # Reduced number for testing
    
    for i in range(num_shapes):
        # Create object with intentional structure
        obj = create_intentional_object(i)
        
        # Save as STL
        save_object_as_stl(obj, f"intentional_shape_{i+1}")
        
        print(f"Completed object {i+1}/{num_shapes}")

if __name__ == "__main__":
    main()