import numpy as np
from numpy import dot, pi, sin, cos, arctan as atan, arccos as acos
from numpy.linalg import norm

def normalize(v):
    n = norm(v)
    if n==0: return v
    else: return v/n

class Angle:
    def degrees_to_radians(degree): return degree*pi/180
    def radians_to_degrees(radian): return radian*180/pi
    def from_radians(radian): return radian
    @classmethod
    def from_degrees(cls, degrees): return cls.degrees_to_radians(degrees)
    def to_radians(angle): return angle
    @classmethod
    def to_degrees(cls, angle): return cls.radians_to_degrees(angle)

class SpherePoint:
    def __init__(self, vector):
        self._vector = normalize(vector)

    @classmethod
    def from_list(cls, l): return cls(np.array(l))
    @classmethod
    def from_vector(cls, v): return cls(v)
    @property
    def vector(self, radius=1): return radius * self._vector
    v = vector
    @property
    def x(self): return self.v[0]
    @property
    def y(self): return self.v[1]
    @property
    def z(self): return self.v[2]

    # Functions for latitude and longitude
    ## ISO Coordinates r, theta, phi
    ## I'm making these helper functions so I can
    ## copy directly from equations on Wikipedia.
    @classmethod
    def _from_ISO_coords(cls, theta, phi):
        x = sin(theta)*cos(phi)
        y = sin(theta)*sin(phi)
        z = cos(theta)
        return cls.from_list([x,y,z])
    @property
    def _ISO_phi(self): return atan(self.y / self.x)
    @property
    def _ISO_theta(self): return acos(self.z)

    ## Colatitude, latitude, longitude getters
    colatitude = _ISO_theta
    @property
    def latitude(self): return pi - self.colatitude
    longitude = _ISO_phi

    ## Abbreviations
    lat = latitude
    lon = longitude
    @property
    def latlon(self): return self.lat, self.lon

    ## Colatitude, latitude, longitude factory methods
    @classmethod
    def from_colatlon(cls, colat, lon):
        theta = colat
        phi = lon
        return cls._from_ISO_coords(theta, phi)
    @classmethod
    def from_latlon(cls, lat, lon):
        colat = pi - lat
        return cls.from_colatlon(colat, lon)

    # Metrics
    def dot(s1, s2): return np.dot(s1.vector, s2.vector)
    cos_between = dot

    def angle_between(s1, s2): return acos(cos_between(s1, s2))
    distance_between = angle_between

    # Functions for combining
    @classmethod
    def reflection(cls, s1, s2):
        v1 = s1.vector
        v2 = s2.vector
        v_reflected = (2*dot(v1, v2)*v2) - v1
        return cls(v_reflected)
    def reflected_across(s1, s2):
        return SpherePoint.reflection(s1, s2)
    @classmethod
    def midpoint(cls, s1, s2): return cls(s1.vector + s2.vector)
    @classmethod
    def barycenter(cls, points): return cls(sum([p.vector for p in points]))


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
    def light_projected_area(self): return self.L.dot(self.N)
    mu_i = light_projected_area
    mu_0 = light_projected_area

    @property
    def viewer_projected_area(self): return self.V.dot(self.N)
    mu_r = viewer_projected_area
    mu = viewer_projected_area
