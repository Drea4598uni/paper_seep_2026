import pyvista as pv

path1 = "yNormal_les.vtp"
path2 = "zNormal_les.vtp"
mesh1 = pv.read(path1)
mesh2 = pv.read(path2)
merged_mesh = mesh1.merge(mesh2)
merged_mesh.save("les_mesh.vtp")
print("Merged mesh saved as 'les_mesh.vtp'")