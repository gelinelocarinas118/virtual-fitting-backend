import bpy, sys, os, json
from mathutils import Vector


argv = sys.argv[sys.argv.index("--") + 1:]
if len(argv) < 2:
    raise SystemExit("Usage: blender ... -- input.obj output.glb [--monochrome R G B]")

in_obj, out_glb, *rest = argv
mono_rgb = None
if "--monochrome" in rest:
    i = rest.index("--monochrome")
    try:
        mono_rgb = tuple(map(float, rest[i + 1 : i + 4]))
    except ValueError:
        raise SystemExit("--monochrome needs three floats R G B (0-1)")


bpy.ops.wm.read_factory_settings(use_empty=True)

bpy.ops.import_scene.obj(filepath=in_obj)
obj = bpy.context.selected_objects[0]


if mono_rgb:
    mat_name = f"Mono_{'_'.join(f'{c:.2f}' for c in mono_rgb)}"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*mono_rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.6

    for ob in bpy.data.objects:
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(mat)
    print(f"[BLENDER] applied monochrome colour {mono_rgb}")


bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB')
if not os.path.isfile(out_glb):
    raise FileNotFoundError(out_glb)
print(f"[BLENDER] GLB written → {out_glb}")
