from numpy import sqrt
from geometry import SpherePoint
from collections import deque

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

class GeoHedron
    def __init__(triangles):
        self.triangles = triangles

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
