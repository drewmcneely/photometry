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
    pass

class Facet:
    # List of Parameters
    # area
    # properties :: MaterialProperty
    # diffuse_fraction
    # specular_fraction
    # diffuse_law
    # specular_law

class ReflectionGeometry:
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

class ModelGeometry:
    # list of facets
