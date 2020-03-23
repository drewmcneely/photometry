import numpy as np
from numpy import dot

import reflectivity_laws as refl
from helpers import *

class MaterialProperty:
    # List of Parameters
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
    # List of Parameters
    # area
    # normal_vector
    # properties :: MaterialProperty
    # diffuse_fraction
    # specular_fraction
    # diffuse_law
    # specular_law

    def __init__(self,
            area=1,
            normal_vector=np.array([1, 0, 0]),
            properties=MaterialProperty(),
            diffuse_fraction=0.5,
            diffuse_law=refl.lambert_diffuse,
            specular_law=refl.blinn_phong_specular
            ):
        self.area = area
        self.normal_vector = normal_vector
        self.properties = properties
        self.diffuse_fraction = diffuse_fraction
        self.specular_fraction = 1-self.diffuse_fraction
        self.diffuse_law = diffuse_law
        self.specular_law = specular_law

    def geometry(self, L, V):
        return FacetGeometry(L, V, self.normal_vector)

    def reflectivity(self, L, V):
        mat = self.properties
        geom = self.geometry(L, V)
        kd = self.diffuse_fraction
        ks = self.specular_fraction
        Rd = self.diffuse_law
        Rs = self.specular_law

        R = kd*Rd(mat, geom) + ks*Rs(mat, geom)
        return R

    def scattering(self, L, V):
        geom = self.geometry(L, V)
        mu = geom.mu
        mu_0 = geom.mu_0

        if mu<0 or mu_0<0:
            return 0
        else:
            R = self.reflectivity(L, V)
            S = mu * mu_0 * R
            return S

class FacetGeometry:
    def __init__(self, L, V, N):
        self.L = L
        self.V = V
        self.N = N

    @property
    def R(self):
        L = self.L
        N = self.N
        return 2*dot(L, N)*N - L

    @property
    def O(self): return self.V

    @property
    def I(self): return self.L

    @property
    def H(self): return normalize(self.L + self.V)

    @property
    def mu_i(self): return dot(self.L, self.N)


    @property
    def mu_r(self): return dot(self.V, self.N)

    @property
    def mu(self): return self.mu_r

    @property
    def mu_0(self): return self.mu_i

    @property
    def theta_i(self): return acos(self.mu_i)

    @property
    def theta_r(self): return acos(self.mu_r)

    @property
    def incidence_angle(self): return self.theta_i

    @property
    def observation_angle(self): return self.theta_r

    @property
    def phase_dot(self): return dot(self.O, self.I)

    @property
    def phase_angle(self): return acos(self.phase_dot)

    @property
    def phi(self): return self.phase_angle

class Model:
    # list of facets
    def __init__(self, facets=[Facet()]):
        self.facets = facets

    def scattering(self, L, V):
        return sum([f.scattering(L,V) for f in self.facets])
