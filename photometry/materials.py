import numpy as np
from numpy import dot

import reflectivity_laws as refl
from geometry import SpherePoint

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

class FacetGeometry:
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
    def R(self): return self.L.reflected_across(self.N)

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
