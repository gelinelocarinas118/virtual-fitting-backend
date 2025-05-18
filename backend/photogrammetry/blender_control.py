import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def adjust_model_in_blender(model_path, output_path, blend_template_path,
                            measurement_json_path, target_height_cm=None):

    script_path = os.path.abspath("photogrammetry/blender_script.py")

    cmd = [
        os.getenv("BLENDER_PATH", "blender"),
        "--factory-startup",
        "-b", blend_template_path,
        "--python", script_path,
        "--",
        model_path,
        output_path,
        measurement_json_path, 
    ]

    if target_height_cm is not None:
        cmd.append(str(target_height_cm))

    print(f"[DEBUG][blender_control] Running Blender command:\n    {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("[DEBUG][blender_control] Blender returned successfully")
