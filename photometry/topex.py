import numpy as np
from pathlib import Path
import pymesh as pm

from operator import itemgetter
from materials import Facet, Model
from geometry import SpherePoint

from visualization import plot_function_triangles as plot

from itertools import islice, repeat

class Topex:
    def __init__(self, mesh):
        attributes = [
                "face_area",
                "face_normal"
                ]
        for a in attributes:
            mesh.add_attribute(a)

        areas = mesh.get_attribute("face_area")
        normals = mesh.get_attribute("face_normal")
        length_to_split = repeat(3, len(areas))
        Inputt = iter(normals)
        normals = [list(islice(Inputt, elem)) for elem in length_to_split]

        normal_directions = [SpherePoint.from_list(n) for n in normals]

        facets = [Facet(area=a, normal_direction=n) for a,n in zip(areas, normal_directions)]
        model = Model(facets)

        self.mesh = mesh
        self.areas = areas
        self.normals = normal_directions
        self.facet_model = model

    @classmethod
    def from_path(cls, path):
        mesh = pm.load_mesh(str(topex_file_path))
        return cls(mesh)

    @property
    def total_area(self): return sum(self.areas)

    def components(self):
        comps = pm.separate_mesh(self.mesh)
        return [Topex(c) for c in comps]

    def reduced(self, n=10):
        components = self.components()

        areas = [c.total_area for c in components]

        area_tuples = zip(components, areas)

        components = sorted(area_tuples, key=itemgetter(1), reverse=True)
        components = components[:10]
        components = [c[0].mesh for c in components]
        mesh = pm.merge_meshes(components)
        return Topex(mesh)

    def scatter(self, light_direction, viewer_direction):
        return self.facet_model.scatter(light_direction, viewer_direction)

    def total_scatter(self, viewer_direction):
        return self.facet_model.total_scatter(viewer_direction)

if __name__ == "__main__":
    #topex_dir = Path('/home/drew/dev/photometry/data/models/topex-poseidon/obj/')
    topex_dir = Path('/home/drew/dev/photometry/photometry/')
    #topex_file_path = topex_dir / "Topex-Posidon-composite.obj"
    topex_file_path = topex_dir / "cube.obj"
    topex = Topex.from_path(topex_file_path)
    #topex = topex.reduced()

    #light_direction = SpherePoint.from_list([1,1,1])
    def func(viewer_direction):
        return topex.total_scatter(viewer_direction)

    plot(func)
