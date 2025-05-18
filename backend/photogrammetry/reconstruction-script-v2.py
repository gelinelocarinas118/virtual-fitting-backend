from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os, subprocess, threading, requests, json
from datetime import datetime

from blender_control import adjust_model_in_blender

# choose one pose estimation method

from mp_pose_est_module import extract_measurements_from_images # mediapipe
# from op_pose_est_module import extract_measurements_from_images # openpose
# from pn_pose_est_module import extract_measurements_from_images # posenet



load_dotenv()
app = Flask(__name__)

MESHROOM_PATH = os.getenv('MESHROOM_PATH')
UPLOAD_DIR    = os.path.abspath(os.getenv('UPLOAD_DIR',   '../storage/app/public/uploads'))
OUTPUT_DIR    = os.path.abspath(os.getenv('OUTPUT_DIR',   '../storage/app/public/outputs'))
CALLBACK_PORT = os.getenv('CALLBACK_PORT', '8000')
MESH_PORT     = int(os.getenv('MESH_PORT', '3001'))

# ─────────────────── 1. ROUTES ─────────────────────────
@app.post("/upload")
def handle_upload_request():
    """
    Expected JSON body:
        {
          "timestamp": "YYYYmmdd_HHMMSS",
          "height": 172      # in cm (integer or numeric string)
        }
    """
    try:
        data       = request.get_json(force=True)
        timestamp  = data.get('timestamp')
        height_raw = data.get('height')    

        if not timestamp:
            return jsonify({'error': 'Missing timestamp'}), 400
        if height_raw is None:
            return jsonify({'error': 'Missing height'}), 400
        try:
            height_cm = int(height_raw)
            if not (50 <= height_cm <= 300):
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Height must be an integer (50-300 cm)'}), 422

        upload_path  = os.path.join(UPLOAD_DIR,  timestamp)
        output_path  = os.path.join(OUTPUT_DIR,  timestamp)
        if not os.path.isdir(upload_path):
            return jsonify({'error': f'Upload directory not found: {upload_path}'}), 404
        os.makedirs(output_path, exist_ok=True)

        threading.Thread(
            target=full_pipeline,
            args=(upload_path, output_path, timestamp, height_cm),
            daemon=True
        ).start()

        return jsonify({'message': 'Reconstruction started.', 'timestamp': timestamp}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─────────────────── 2. HELPERS ─────────────────────────
def find_image(path, basename):
    for ext in ('.jpg', '.jpeg', '.png'):
        candidate = os.path.join(path, f"{basename}{ext}")
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(f'{basename} image (.jpg|.jpeg|.png) not found in {path}')
# BG removel
from rembg import remove
from PIL import Image
import io, pathlib

def remove_background(src_path: str, dst_path: str):
    """
    Loads an image (PNG/JPG), removes the background with rembg,
    and saves the result as a PNG with an alpha channel.
    """
    with open(src_path, "rb") as f:
        input_bytes = f.read()
    output = remove(input_bytes)      
    Image.open(io.BytesIO(output)).save(dst_path, "PNG")
    print(f"[INFO] Background removed → {dst_path}")
    return dst_path


# ─────────────────── 3. MAIN PIPELINE ───────────────────
def full_pipeline(input_path, output_path, timestamp, height_cm):
    callback_url = f"http://localhost:{CALLBACK_PORT}/api/photogrammetry/callback"
    status, message = 'success', ''

    try:
        #  Pose estimation & measurements
        front_img = find_image(input_path, 'front')
        side_img  = find_image(input_path, 'side')

        measurements = extract_measurements_from_images(front_img, side_img, height_cm)
        measurements['height_cm'] = height_cm

        measurement_file = os.path.join(output_path, f"{timestamp}_measurements.json")
        with open(measurement_file, 'w') as f:
            json.dump(measurements, f, indent=2)
        print(f"[INFO] Measurements saved → {measurement_file}")

        # Photogrammetry (runs Meshroom)
        subprocess.run(
            [MESHROOM_PATH, "--input", input_path, "--output", output_path],
            check=True
        )

        # Locate reconstructed mesh (OBJ only)
        model_path = os.path.join(output_path, 'texturedMesh.obj')
        if not os.path.isfile(model_path):
            raise FileNotFoundError("Meshroom output (.obj) not found")
        print(f"[DEBUG] Found mesh → {model_path}")

        # Call Blender, passing the measurement JSON + height
        glb_out         = os.path.join(output_path, f"{timestamp}_model.glb")
        blend_template  = os.path.abspath("photogrammetry/base.blend")

        print(f"[DEBUG] About to run Blender with:\n"
              f"       model: {model_path}\n"
              f"   output_glb: {glb_out}\n"
              f"measure_json: {measurement_file}\n"
              f"   height_cm: {height_cm}")

        adjust_model_in_blender(
            model_path=model_path,
            output_path=glb_out,
            blend_template_path=blend_template,
            measurement_json_path=measurement_file,
            target_height_cm=height_cm
        )
        print(f"[INFO] GLB exported → {glb_out}")
        message = 'Model reconstructed, scaled, and exported to GLB.'

    except subprocess.CalledProcessError as e:
        status  = 'error'
        message = f'Meshroom/Blender failed: {e}'
    except Exception as e:
        status  = 'exception'
        import traceback
        tb = traceback.format_exc()
        message = f'Unexpected error: {e}\n{tb}'
        print(f"[ERROR] full_pipeline exception:\n{tb}")

    # Callback Laravel
    try:
        res = requests.post(callback_url, json={
            'timestamp': timestamp,
            'status':    status,
            'message':   message
        })
        print(f"[CALLBACK] {status} — Laravel responded {res.status_code}")
        if status != 'success':
            print(f"[CALLBACK MESSAGE] {message}")
    except Exception as e:
        print(f"[CALLBACK ERROR] {e}")

# ─────────────────── 4. ENTRY ───────────────────────────
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=MESH_PORT)
