import numpy as np
from pathlib import Path
import pymesh as pm

from operator import itemgetter

topex_dir = Path('/home/drew/dev/photometry/models/topex-poseidon/obj/')
topex_file_path = topex_dir / "Topex-Posidon-composite.obj"

mesh = pm.load_mesh(str(topex_file_path))

components = pm.separate_mesh(mesh)

attributes = [
        "face_area",
        "face_normal"
        ]

for c in components:
    for a in attributes:
        c.add_attribute(a)

areas = [sum(c.get_attribute("face_area")) for c in components]

area_tuples = zip(components, areas)

components = sorted(area_tuples, key=itemgetter(1), reverse=True)

#def face_vertices_from_indices(face_list, vertex_list):
#    return [vertex_list[i] for i in face_list]
#
#def edges_from_vertices(face):
#    v1 = face[1] - face[0]
#    v2 = face[2] - face[0]
#    return (v1, v2)
#
#def wedge_from_edges(edge1, edge2):
#    return 0.5 * np.cross(edge1, edge2)
