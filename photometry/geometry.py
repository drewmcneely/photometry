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

import progressbar as pb
import numpy as np
from numpy import array, dot as npdot, pi, sin, cos, arctan2, arccos, sqrt
from numpy.linalg import norm

from collections import deque

import geojson as gj

import shapely.geometry as sg

def normalize(v):
    n = norm(v)
    if n==0: return v
    else: return v/n

flatten = lambda l: [item for sublist in l for item in sublist]

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
        if not isinstance(vector, np.ndarray):
            print("SpherePoint")
            print(vector, " is the wrong type!")
            print(type(vector))
            raise AttributeError
        elif (not vector.shape==(3,)):
            print("SpherePoint")
            print(vector, " is the wrong length!")
            raise AttributeError
        self._vector = normalize(vector)

    def __str__(self): return "SpherePoint with vector " + str(self.vector)

    @classmethod
    def north_pole(cls): return cls.from_list([0,0,1])
    @classmethod
    def south_pole(cls): return cls.from_list([0,0,-1])

    @classmethod
    def from_list(cls, l): return cls(array(l))
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

    def rotated_by(self, R):
        v = self.vector
        v1 = R.rotate_vector(v)
        return SpherePoint(v1)

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
    def dot(s1, s2):
        real = npdot(s1.vector, s2.vector)
        return real
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

class SphereTriangle:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def __str__(self):
        strs = (str(self.p1), str(self.p2), str(self.p3))
        return "%s\n%s\n%s\n" % strs

    @classmethod
    def from_points_list(cls, points): 
        return cls(*points)

    @classmethod
    def from_indices(cls, indices, points):
        ps = [points[i] for i in indices]
        return cls.from_points_list(ps)

    @property
    def points(self): return [self.p1, self.p2, self.p3]
    
    @property
    def point_matrix(self):
        vs = [p.vector for p in self.points]
        M = np.array(vs).T
        return M

    @property
    def divided(self):
        """Take a SphereTriangle and return a list of 4 SphereTriangles
        making a "triforce" pattern.
        """

        ps = deque(self.points)
        pr = ps.copy()
        pr.rotate(-1)

        mids = deque([SpherePoint.midpoint(s,r) for s,r in zip(ps, pr)])
        midr = mids.copy()
        midr.rotate()
        tris = [SphereTriangle(*z) for z in zip(ps, mids, midr)]
        return tris + [SphereTriangle(*mids)]

    @property
    def barycenter(self): return SpherePoint.barycenter(self.points)

    @property
    def earth_coordinate_triad(self):
        ps = self.points
        coords = [p.earth_coordinates for p in ps]
        return coords

    @property
    def geojson_coordinate_ring(self):
        ps = self.points
        point_ring = [ps[i] for i in [0,2,1,0]]
        coords = [p.earth_coordinates for p in point_ring]
        return coords

    @property
    def geojson_polygon(self):
        return gj.Polygon([self.geojson_coordinate_ring])

    @property
    def v1_minus_cross(self):
        v1 = self.p1.vector
        v2 = self.p2.vector
        v3 = self.p3.vector

        a = v2 - v1
        b = v3 - v1
        n = normalize(np.cross(a,b))
        should_be_0 = diff = norm(v1 - n)
        return should_be_0

    @property
    def is_clockwise(self):
        if np.abs(self.v1_minus_cross) > .4: return False
        else: return True

    def geojson_feature(self, ident):
        return gj.Feature(geometry=self.geojson_polygon, id=ident)

    def rotated_by(self, R):
        ps = [p.rotated_by(R) for p in self.points]
        return SphereTriangle.from_points_list(ps)

    def mapf(t, f): return f(t.barycenter)

class IcoSphere:
    def __init__(self, triangles):
        self.triangles = triangles

    def __str__(self):
        s = ""
        for i, t in enumerate(self.triangles):
            s += str(i) + "\n" + str(t) + "\n\n"
        return s

    @property
    def north_poles(self):
        pole = SpherePoint.north_pole()
        return [point_is_inside_triangle(pole, t) for t in self.triangles]

    @property
    def south_poles(self):
        pole = SpherePoint.south_pole()
        return [point_is_inside_triangle(pole, t) for t in self.triangles]

    @property
    def divided_once(self):
        return IcoSphere(flatten([tri.divided for tri in self.triangles]))

    def divided(self, n=1):
        if n<=0: return self
        else: return self.divided_once.divided(n-1)

    @classmethod
    def from_triangle_list(cls, triangles):
        return cls(triangles)

    @classmethod
    def sphere(cls):
        s = cls.icosahedron().divided(3)
        return s

    @property
    def points(self):
        return flatten([t.points for t in self.triangles])

    def reduced(self, t=5):
        tris = self.triangles
        print(len(tris))
        newtris = [tris[t]]
        return IcoSphere(newtris)

    @property
    def barycenters(self):
        return [tri.barycenter for tri in self.triangles]

    @property
    def point_lats(self):
        return [p.earth_latitude for p in self.points]
    @property
    def point_lons(self):
        return [p.earth_longitude for p in self.points]

    @property
    def bary_lats(self):
        return [b.earth_latitude for b in self.barycenters]
    @property
    def bary_lons(self):
        return [b.earth_longitude for b in self.barycenters]

    @property
    def is_clockwise(self):
        if all([t.is_clockwise for t in self.triangles]): return True
        else: return False

    def mapf(s, f):
        results = []
        for t in pb.progressbar(s.triangles):
            results += [t.mapf(f)]
        return results

    @classmethod
    def icosahedron(cls):
        t = (1.0 + sqrt(5.0)) / 2.0;
        a = 0

        vectors = [
            [-1,  t,  a],
            [ 1,  t,  a],
            [-1, -t,  a],
            [ 1, -t,  a],
            [ a, -1,  t],
            [ a,  1,  t],
            [ a, -1, -t],
            [ a,  1, -t],
            [ t,  a, -1],
            [ t,  a,  1],
            [-t,  a, -1],
            [-t,  a,  1]
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

        tris = [SphereTriangle.from_indices(idx, points) for idx in idxs]
        return cls(tris)

    @property
    def geojson(self):
        """ Return a python object corresponding to a GeoJSON.

        Output should look like:
        return {
            "type" : "FeatureCollection",
            "features" : [A]
            }

        where an example A would look like
        A = {
            "type": "Feature",
            "properties": {
                "GEO_ID": "0500000US01001",
                "STATE": "01",
                "COUNTY": "001",
                "NAME": "Autauga",
                "LSAD": "County",
                "CENSUSAREA": 594.436
                },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon1, lat1],
                    [lon2, lat2], ...
                    ]]
                }
            "id": "01001"
            }
        """

        e = enumerate(self.triangles)
        features = [t.geojson_feature(ident=i) for (i,t) in e]
        return gj.FeatureCollection(features)
    def rotated_by(self, R):
        ts = [t.rotated_by(R) for t in self.triangles]
        return IcoSphere.from_triangle_list(ts)

class Rotation:
    def __init__(self, R):
        self.R = R
    @property
    def matrix(self): return self.R

    def two_dim(angle):
        s = sin(angle)
        c = cos(angle)
        R = np.array([[c, -s], [s, c]])
        return R

    @classmethod
    def x(cls, angle):
        s = sin(angle)
        c = cos(angle)
        R = np.array([
            [1, 0, 0],
            [0, c,-s],
            [0, s, c]])
        return cls(R)

    @classmethod
    def y(cls, angle):
        s = sin(angle)
        c = cos(angle)
        R = np.array([
            [c, 0, s],
            [0, 1, 0],
            [-s,0, c]])
        return cls(R)

    @classmethod
    def z(cls, angle):
        s = sin(angle)
        c = cos(angle)
        R = np.array([
            [c,-s, 0],
            [s, c, 0],
            [0, 0, 1]])
        return cls(R)

    @classmethod
    def identity(cls): return cls(np.identity(3))

    @classmethod
    def for_icosphere(cls):
        a = Angle.from_degrees(5)
        y = cls.y(a)
        z = cls.z(a)
        return y.compose(z)

    def compose(A, B): return Rotation(B.matrix @ A.matrix)
    def rotate_vector(self, v): return self.matrix @ v

def point_is_inside_triangle(point, triangle):
    print("Here!")
    M = triangle.point_matrix
    p = point.vector
    a = np.linalg.inv(M) @ p
    lam = 1/sum(a)
    return (lam > 0)
