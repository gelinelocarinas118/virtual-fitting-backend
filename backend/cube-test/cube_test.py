from pathlib import Path
from os import getenv

from csm import CSMClient
from dotenv import load_dotenv   # pip install python-dotenv

# Load .env file into process-level env vars
load_dotenv()                    # looks for .env in the cwd by default

API_KEY = getenv("CUBE_API_KEY")  # make sure .env has CSM_API_KEY=...
csm_client = CSMClient(api_key=API_KEY)

# input a local image path (also supported: url, PIL.Image.Image)
image_path = r"C:\Users\family\Desktop\sides\project1\backend\cube-test\front.png"
result = csm_client.image_to_3d(image_path, mesh_format='glb')

print(result.mesh_path)