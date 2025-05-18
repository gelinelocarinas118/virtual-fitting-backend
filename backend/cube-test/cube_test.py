from csm import CSMClient

csm_client = CSMClient(api_key='8c6420F4611914534F1fF65E2dF3d570')

# input a local image path (also supported: url, PIL.Image.Image)
image_path = r"C:\Users\family\Desktop\sides\project1\backend\cube-test\front.png"
result = csm_client.image_to_3d(image_path, mesh_format='glb')

print(result.mesh_path)