import numpy as np
from numpy import dot

import reflectivity_laws as refl
from helpers import *
from geometry import SpherePoint, FacetGeometry

class MaterialProperty:
    # List of attributes used in reflectivity_laws:
    # rho
    # E_0
    # color: Color vector
    # sigma
    # F_0: Normal Fresnel reflectance
    # alpha: Phong shininess constant
    # lobe_radius: angle defining a specular lobe
    # pomega_0: single scattering albedo
    def __init__(self, rho=1, alpha=2):
        self.rho=rho
        self.alpha=alpha

class Facet:
    def __init__(self,
            area=1,
            normal_direction=SpherePoint.from_list([1,0,0])
            material_property=MaterialProperty(),
            diffuse_fraction=0.5,
            diffuse_law=refl.lambert_diffuse,
            specular_law=refl.blinn_phong_specular
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

    @property
    def reflectivity_law(self, mat, geom):
        d = self.d
        s = self.s
        Rd = self.diffuse_law(mat, geom)
        Rs = self.specular_law(mat, geom)
        return d*Rd + s*Rs

    def scattering_law(self, mat, geom):
        R = self.reflectivity_law
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
        geom = FacetGeometry(light_direction, viewer_direction, self.normal_direction)
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
