import numpy as np
from dataclasses import dataclass


@dataclass()
class Point:
    x: float
    y: float
    z: float


@dataclass()
class Line:
    p0: np.array
    p1: np.array

    def x(self, t):
        p0, p1 = self.p0, self.p1
        return p0.x + (p1.x - p0.x) * t

    def y(self, t):
        p0, p1 = self.p0, self.p1
        return p0.y + (p1.y - p0.y) * t

    def z(self, t):
        p0, p1 = self.p0, self.p1
        return p0.z + (p1.z - p0.z) * t

    def point(self, t):
        return Point(self.x(t), self.y(t), self.z(t))

    def top_intersection(self):
        p0, p1 = self.p0, self.p1

        # Solve z = 0.5 for t.
        t = (0.5 - p0.z) / (p1.z - p0.z)

        x = self.x(t)
        if not (-0.5 <= self.x(t) <= 0.5):
            return None

        y = self.y(t)
        if not (-0.5 <= self.y(t) <= 0.5):
            return None

        return Point(x, y, self.z(t))

    def bottom_intersection(self):
        p0, p1 = self.p0, self.p1
        t = (-0.5 - p0.z) / (p1.z - p0.z)

        x = self.x(t)
        if not (-0.5 <= self.x(t) <= 0.5):
            return None

        y = self.y(t)
        if not (-0.5 <= self.y(t) <= 0.5):
            return None

        return Point(x, y, self.z(t))

    def left_intersection(self):
        p0, p1 = self.p0, self.p1
        t = (-0.5 - p0.x) / (p1.x - p0.x)

        y = self.y(t)
        if not (-0.5 <= self.y(t) <= 0.5):
            return None

        z = self.z(t)
        if not (-0.5 <= self.z(t) <= 0.5):
            return None

        return Point(self.x(t), y, z)

    def right_intersection(self):
        p0, p1 = self.p0, self.p1
        t = (0.5 - p0.x) / (p1.x - p0.x)

        y = self.y(t)
        if not (-0.5 <= self.y(t) <= 0.5):
            return None

        z = self.z(t)
        if not (-0.5 <= self.z(t) <= 0.5):
            return None

        return Point(self.x(t), y, z)

    def front_intersection(self):
        p0, p1 = self.p0, self.p1
        t = (-0.5 - p0.y) / (p1.y - p0.y)

        x = self.x(t)
        if not (-0.5 <= self.x(t) <= 0.5):
            return None

        z = self.z(t)
        if not (-0.5 <= self.z(t) <= 0.5):
            return None

        return Point(x, self.y(t), z)

    def back_intersection(self):
        p0, p1 = self.p0, self.p1
        t = (0.5 - p0.y) / (p1.y - p0.y)

        x = self.x(t)
        if not (-0.5 <= self.x(t) <= 0.5):
            return None

        z = self.z(t)
        if not (-0.5 <= self.z(t) <= 0.5):
            return None

        return Point(x, self.y(t), z)

    def ray_length(self):
        points = []

        for maybe_intersection in [
            self.top_intersection,
            self.bottom_intersection,
            self.left_intersection,
            self.right_intersection,
            self.front_intersection,
            self.back_intersection,
        ]:
            if p := maybe_intersection():
                points.append(p)
                if len(points) == 2:
                    break

        x = points[1].x - points[0].x
        y = points[1].y - points[0].y
        z = points[1].z - points[0].z
        return np.sqrt(x * x + y * y + z * z)


class Cube:
    @staticmethod
    def random_point() -> Point:
        return Point(*np.random.uniform(-0.5, 0.5, 3))


class Universe:
    radius: float = 10000.0
    sample_cube: tuple[float, float] = (-10000.0, 10000.0)

    @classmethod
    def random_point(cls) -> Point:
        while True:
            points = np.random.uniform(cls.sample_cube[0], cls.sample_cube[1], 3)
            if np.sqrt(np.sum([point * point for point in points])) <= cls.radius:
                return Point(*points)


if __name__ == "__main__":
    trials = 1000000
    total = 0.0
    for _ in range(trials):
        total += Line(Universe.random_point(), Cube.random_point()).ray_length()

    print("average ray length:", total / trials)
