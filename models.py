'''
photometry.py. Visualize the photometric output of a Wavefront obj. model.
Copyright (C) 2020  Drew Allen McNeely

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import numpy as np
from numpy import dot

from geometry import SpherePoint
from materials import MaterialProperty, lambert_diffuse, blinn_phong_specular

import pymesh as pm

from itertools import islice, repeat

class ReflectionGeometry:
    def __init__(self, light_direction, viewer_direction, surface_normal):
        self._light = light_direction
        self._view = viewer_direction
        self._normal = surface_normal

    @property
    def light_direction(self): return self._light
    incidence_direction = light_direction
    L = light_direction
    I = light_direction
    E_0 = light_direction

    @property
    def viewer_direction(self): return self._view
    observation_direction = viewer_direction
    V = viewer_direction
    O = viewer_direction
    E = viewer_direction

    @property
    def surface_normal(self): return self._normal
    N = surface_normal

    @property
    def reflected_direction(self): return self.L.reflected_across(self.N)
    R = reflected_direction

    @property
    def H(self): return SpherePoint.midpoint(self.L, self.V)


    # Angles
    @property
    def incidence_angle(self): return SpherePoint.angle_between(self.N, self.I)
    light_angle = incidence_angle
    theta_i = incidence_angle
    theta_0 = incidence_angle

    @property
    def observation_angle(self): return SpherePoint.angle_between(self.N, self.O)
    viewer_angle = observation_angle
    theta_r = observation_angle
    theta = observation_angle

    @property
    def phase_angle(self): return SpherePoint.angle_between(self.O, self.I)
    phi = phase_angle
    alpha = phase_angle

    # Projections
    @property
    def light_projected_area(self): 
        L = self.L
        N = self.N
        l = L.dot(N)
        return l

    @property
    def mu_i(self): return self.light_projected_area
    @property
    def mu_0(self): return self.light_projected_area

    @property
    def viewer_projected_area(self): return self.V.dot(self.N)
    mu_r = viewer_projected_area
    mu = viewer_projected_area

class Facet:
    def __init__(self,
            area=1,
            normal_direction=SpherePoint.from_list([1,0,0]),
            material_property=MaterialProperty(),
            diffuse_fraction=0.5,
            diffuse_law=lambert_diffuse,
            specular_law=blinn_phong_specular
            ):
        self.area = area
        self.normal_direction = normal_direction
        self.material_property = material_property
        self.diffuse_fraction = diffuse_fraction
        self.specular_fraction = 1-self.diffuse_fraction
        self.diffuse_law = diffuse_law
        self.specular_law = specular_law

    @property
    def k_d(self): return self.diffuse_fraction
    d = k_d

    @property
    def k_s(self): return self.specular_fraction
    s = k_s

    def reflectivity_law(self, mat, geom):
        d = self.d
        s = self.s
        Rd = self.diffuse_law(mat, geom)
        Rs = self.specular_law(mat, geom)
        return d*Rd + s*Rs

    def scattering_law(self, mat, geom):
        mu = geom.mu
        mu_0 = geom.mu_0
        if mu<0 or mu_0<0:
            S = 0
        else:
            R = self.reflectivity_law
            S = self.area * mu * mu_0 * R(mat, geom)
        return S

    def mat_geom_pair(self, light_direction, viewer_direction):
        mat = self.material_property
        geom = ReflectionGeometry(light_direction, viewer_direction, self.normal_direction)
        return (mat, geom)

    def scatter(self, light_direction, viewer_direction):
        s = self.scattering_law
        mgpair = self.mat_geom_pair(light_direction, viewer_direction)
        return s(*mgpair)

class Model:
    # list of facets
    def __init__(self, facets=[Facet()]):
        self.facets = facets

    def scatter(self, light_direction, viewer_direction):
        scatters = [f.scatter(light_direction, viewer_direction) for f in self.facets]
        return sum(scatters)

    def total_scatter(self, viewer_direction):
        return self.scatter(viewer_direction, viewer_direction)

class WavefrontModel:
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
        mesh = pm.load_mesh(str(path))
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
