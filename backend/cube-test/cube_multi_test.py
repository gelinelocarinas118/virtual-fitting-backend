import os
from pathlib import Path
from os import getenv

from csm import CSMClient
from dotenv import load_dotenv   # pip install python-dotenv

load_dotenv()  # load .env file from current dir

API_KEY = getenv("CUBE_API_KEY")  # your .env must have CUBE_API_KEY=...

csm_client = CSMClient(api_key=API_KEY)

folder = Path(r"C:\Users\family\Desktop\sides\backend\cube-test\background_removed")
image_paths = [folder / f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]

mesh_files = []
for img in image_paths:
    print(f"Processing {img} ...")
    result = csm_client.image_to_3d(str(img), mesh_format='glb')  # convert Path to str for API
    mesh_files.append(result.mesh_path)

print("All done! Generated meshes:", mesh_files)
