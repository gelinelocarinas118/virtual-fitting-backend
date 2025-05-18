import bpy
import sys
import json
import os

argv = sys.argv[sys.argv.index("--") + 1:]
model_path, landmarks_json, camera_json, output_path = argv

# Load model
bpy.ops.import_scene.obj(filepath=model_path)

# Load landmarks
with open(landmarks_json, 'r') as f:
    landmarks = json.load(f)

# Try to load camera data
if os.path.exists(camera_json):
    with open(camera_json, 'r') as f:
        camera_params = json.load(f)

    # Create and configure camera
    cam = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("CameraObj", cam)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    cam.lens = float(camera_params.get('focal_length', 35.0))  # Default fallback
    cam.sensor_width = float(camera_params.get('sensor_size', [36])[0])
    cam_obj.location = (0, -3, 1.5)
else:
    print(f"[WARN] Camera JSON not found at {camera_json}. Skipping camera setup.")

# TODO: apply transformations using landmarks if needed

# Export as GLB
bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
