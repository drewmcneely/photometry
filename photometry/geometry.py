from numpy import array, dot as npdot, pi, sin, cos, arctan2, arccos, sqrt
from numpy.linalg import norm

from collections import deque

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
    def _ISO_phi(self): return arctan2(self.y, self.x)
    @property
    def _ISO_theta(self): return arccos(self.z)

    ## Colatitude, latitude, longitude getters
    colatitude = _ISO_theta

    @property
    def latitude(self): return Angle.from_degrees(90.0) - self.colatitude

    @property
    def earth_latitude(self): return Angle.to_degrees(self.latitude)

    longitude = _ISO_phi

    @property
    def earth_longitude(self): return Angle.to_degrees(self.longitude)

    @property
    def earth_coordinates(self): return (self.earth_longitude, self.earth_latitude)

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
    def dot(s1, s2): return npdot(s1.vector, s2.vector)
    cos_between = dot

    def angle_between(s1, s2): return acos(cos_between(s1, s2))
    distance_between = angle_between

    # Functions for combining
    @classmethod
    def reflection(cls, s1, s2):
        v1 = s1.vector
        v2 = s2.vector
        v_reflected = (2*npdot(v1, v2)*v2) - v1
        return cls(v_reflected)
    def reflected_across(s1, s2):
        return SpherePoint.reflection(s1, s2)
    @classmethod
    def midpoint(cls, s1, s2): return cls(s1.vector + s2.vector)
    @classmethod
    def barycenter(cls, points): return cls(sum([p.vector for p in points]))

class Triangle:
    def __init__(p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    @classmethod
    def from_points(cls, points): return cls(*points)

    @classmethod
    def from_indices(cls, indices, points):
        return cls.from_points([points[i] for i in indices])

    @property
    def points(self): return [self.p1, self.p2, self.p3]

    @property
    def divided(self):
        """Take a Triangle and return a list of 4 Triangles
        making a "triforce" pattern.
        """

        ps = deque(self.points)
        pr = ps.copy()
        pr.rotate(-1)

        mids = deque([s.midpoint(r) for s,r in zip(ps, pr)])
        midr = mids.copy()
        midr.rotate()
        tris = [Triangle(*z) for z in zip(ps, mids, midr)]
        return tris + [Triangle(*mids)]

    @property
    def barycenter(self): return SpherePoint.barycenter(self.points)

    @property
    def earth_coordinates(self):
        ps = self.points
        point_ring = [ps[i] for i in [0,1,2,0]]
        coords = [p.earth_coordinates for p in point_ring]
        return [coords]

class GeoHedron
    def __init__(triangles):
        self.triangles = triangles

    @property
    def divided_once(self):
        return GeoHedron(sum([tri.divided for tri in self.triangles]))

    def divided(self, n):
        if n<=0: return self
        else: return self.divided_once.divided(n-1)

    @classmethod
    def sphere(cls):
        return cls.icosahedron.divided(1)

    @property
    def barycenters(self):
        return [tri.barycenter for tri in self.triangles]

    @classmethod
    def icosahedron(cls):
        t = (1.0 + sqrt(5.0)) / 2.0;

        vectors = [
            [-1,  t,  0],
            [ 1,  t,  0],
            [-1, -t,  0],
            [ 1, -t,  0],
            [ 0, -1,  t],
            [ 0,  1,  t],
            [ 0, -1, -t],
            [ 0,  1, -t],
            [ t,  0, -1],
            [ t,  0,  1],
            [-t,  0, -1],
            [-t,  0,  1]
            ]
        points = [SpherePoint.from_list(l) for l in vectors]

        idxs = [
            [0, 11, 5],
            [0, 5, 1],
            [0, 1, 7],
            [0, 7, 10],
            [0, 10, 11],
            [1, 5, 9],
            [5, 11, 4],
            [11, 10, 2],
            [10, 7, 6],
            [7, 1, 8],
            [3, 9, 4],
            [3, 4, 2],
            [3, 2, 6],
            [3, 6, 8],
            [3, 8, 9],
            [4, 9, 5],
            [2, 4, 11],
            [6, 2, 10],
            [8, 6, 7],
            [9, 8, 1]
            ]

        tris = [Triangle.from_indices(idx, points) for idx in idxs]
        return cls(tris)
