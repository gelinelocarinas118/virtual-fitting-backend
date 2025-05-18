# cube_csm.py
import os, requests, pathlib

CUBE_API   = "https://api.csm.ai/v1"
CUBE_TOKEN = os.getenv("CUBE_API_KEY")

def upload_glb_to_cube(glb_path: str, name: str):
    """
    Upload a GLB to Cube CSM.
    Returns (asset_id, file_url).
    """
    if not CUBE_TOKEN:
        raise RuntimeError("CUBE_API_KEY not set in environment")

    headers = {"Authorization": f"Bearer {CUBE_TOKEN}"}
    with open(glb_path, "rb") as f:
        files = {"file": (pathlib.Path(glb_path).name, f, "model/gltf-binary")}
        data  = {"name": name}
        r = requests.post(f"{CUBE_API}/asset", headers=headers,
                          files=files, data=data, timeout=60)
        r.raise_for_status()
    payload = r.json()
    return payload["id"], payload.get("fileUrl")
