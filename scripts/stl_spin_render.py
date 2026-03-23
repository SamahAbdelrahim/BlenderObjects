"""
Shared STL → rotating MP4 pipeline (Blender/bpy). Imported by entrypoint scripts at repo root.
"""
import bpy
import os
from math import radians
from pathlib import Path
import bmesh
from mathutils import Vector

import addon_utils

addon_utils.enable("io_mesh_stl")

frames = 120
fps = 30
resolution = (512, 512)
rotation_axis = "Z"
animation_length_seconds = 4
degrees_to_rotate = 360
output_format = "MPEG4"
video_codec = "H264"
file_format = "FFMPEG"


def _apply_render_settings():
    bpy.context.scene.render.image_settings.file_format = file_format
    bpy.context.scene.render.fps = fps
    bpy.context.scene.render.resolution_x = resolution[0]
    bpy.context.scene.render.resolution_y = resolution[1]
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.ffmpeg.format = output_format
    bpy.context.scene.render.ffmpeg.codec = video_codec
    bpy.context.scene.render.ffmpeg.constant_rate_factor = "HIGH"
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 32
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.view_settings.exposure = 1.0


_apply_render_settings()


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)


def center_and_scale_object(obj, target_size=2.0):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    if bm.verts:
        verts = [v.co.copy() for v in bm.verts]
        min_x = min(v.x for v in verts)
        max_x = max(v.x for v in verts)
        min_y = min(v.y for v in verts)
        max_y = max(v.y for v in verts)
        min_z = min(v.z for v in verts)
        max_z = max(v.z for v in verts)
        center = Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
        dimensions = Vector((max_x - min_x, max_y - min_y, max_z - min_z))
        max_dim = max(dimensions.x, dimensions.y, dimensions.z)
        for v in bm.verts:
            v.co -= center
        if max_dim > 0:
            scale_factor = target_size / max_dim
            for v in bm.verts:
                v.co *= scale_factor
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return target_size


def setup_scene(obj, object_size):
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    distance = object_size * 3.0
    cam.location = (distance * 0.8, -distance * 0.8, object_size * 0.2)
    direction = Vector((0, 0, 0)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 50
    cam.data.clip_end = 1000
    setup_lighting(object_size)
    setup_world_background()
    apply_material(obj)


def setup_lighting(object_size):
    distance = object_size * 4
    main_light_data = bpy.data.lights.new(name="MainLight", type="SUN")
    main_light_data.energy = 10
    main_light = bpy.data.objects.new(name="MainLight", object_data=main_light_data)
    bpy.context.collection.objects.link(main_light)
    main_light.location = (distance, -distance, distance)
    main_light.rotation_euler = (radians(45), 0, radians(45))
    fill_light_data = bpy.data.lights.new(name="FillLight", type="SUN")
    fill_light_data.energy = 8
    fill_light = bpy.data.objects.new(name="FillLight", object_data=fill_light_data)
    bpy.context.collection.objects.link(fill_light)
    fill_light.location = (-distance, distance, distance * 0.5)
    fill_light.rotation_euler = (radians(30), 0, radians(-135))
    top_light_data = bpy.data.lights.new(name="TopLight", type="SUN")
    top_light_data.energy = 6
    top_light = bpy.data.objects.new(name="TopLight", object_data=top_light_data)
    bpy.context.collection.objects.link(top_light)
    top_light.location = (0, 0, distance * 2)
    top_light.rotation_euler = (0, 0, 0)
    front_light_data = bpy.data.lights.new(name="FrontLight", type="SUN")
    front_light_data.energy = 5
    front_light = bpy.data.objects.new(name="FrontLight", object_data=front_light_data)
    bpy.context.collection.objects.link(front_light)
    front_light.location = (0, -distance, 0)
    front_light.rotation_euler = (radians(90), 0, 0)


def setup_world_background():
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    bg_node = nodes.new(type="ShaderNodeBackground")
    bg_node.inputs[0].default_value = (0.1, 0.3, 0.8, 1)
    bg_node.inputs[1].default_value = 1.0
    output_node = nodes.new(type="ShaderNodeOutputWorld")
    world.node_tree.links.new(bg_node.outputs[0], output_node.inputs[0])


def apply_material(obj):
    mat = bpy.data.materials.new(name="ObjectMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
    principled.inputs["Metallic"].default_value = 0.0
    principled.inputs["Roughness"].default_value = 0.6
    try:
        principled.inputs["Specular IOR Level"].default_value = 1.0
    except KeyError:
        try:
            principled.inputs["Specular"].default_value = 1.0
        except KeyError:
            pass
    output = nodes.new(type="ShaderNodeOutputMaterial")
    links.new(principled.outputs[0], output.inputs[0])
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def animate_rotation(obj, total_frames):
    obj.rotation_mode = "XYZ"
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    obj.keyframe_insert(data_path="location", frame=1)
    if rotation_axis == "X":
        obj.rotation_euler = (radians(degrees_to_rotate), 0, 0)
    elif rotation_axis == "Y":
        obj.rotation_euler = (0, radians(degrees_to_rotate), 0)
    else:
        obj.rotation_euler = (0, 0, radians(degrees_to_rotate))
    obj.keyframe_insert(data_path="rotation_euler", frame=total_frames)
    obj.keyframe_insert(data_path="location", frame=total_frames)
    if obj.animation_data:
        for fcurve in obj.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "LINEAR"


def render_video(output_path):
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(animation=True)


def main(input_folder: str, output_folder: str):
    """Walk input_folder for .stl (any depth), mirror relative paths under output_folder."""
    os.makedirs(output_folder, exist_ok=True)
    input_folder = os.path.abspath(input_folder)
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if not filename.lower().endswith(".stl"):
                continue
            stl_path = os.path.join(root, filename)
            rel_dir = os.path.relpath(root, input_folder)
            if rel_dir in (os.curdir, ".", ""):
                output_subfolder = output_folder
            else:
                output_subfolder = os.path.join(output_folder, rel_dir)
            os.makedirs(output_subfolder, exist_ok=True)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_subfolder, base_name + ".mp4")
            print(f"Processing {stl_path}")
            clear_scene()
            bpy.ops.import_mesh.stl(filepath=stl_path)
            obj = bpy.context.selected_objects[0]
            object_size = center_and_scale_object(obj, target_size=2.0)
            setup_scene(obj, object_size)
            animate_rotation(obj, frames)
            render_video(output_path)
            print(f"✅ Rendered: {output_path}")
    print("✅ All STL files processed.")
