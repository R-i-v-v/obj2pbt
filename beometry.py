from __future__ import division
import numpy as np
from math import cos, sin, pi, sqrt, atan2

d2r = pi / 180


class Geometry(object):
    def circle_intersection(self, circle1, circle2):
        '''
        @summary: calculates intersection points of two circles
        @param circle1: tuple(x,y,radius)
        @param circle2: tuple(x,y,radius)
        @result: tuple of intersection points (which are (x,y) tuple)
        '''
        x1, y1, r1 = circle1
        x2, y2, r2 = circle2
        dx, dy = x2 - x1, y2 - y1
        d = sqrt(dx * dx + dy * dy)
        if d > r1 + r2:
            print("#1")
            return None  # no solutions, the circles are separate
        if d < abs(r1 - r2):
            print("#2")
            return None  # no solutions because one circle is contained within the other
        if d == 0 and r1 == r2:
            print("#3")
            return None  # circles are coincident and there are an infinite number of solutions

        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
        h = sqrt(r1 * r1 - a * a)
        xm = x1 + a * dx / d
        ym = y1 + a * dy / d
        xs1 = xm + h * dy / d
        xs2 = xm - h * dy / d
        ys1 = ym - h * dx / d
        ys2 = ym + h * dx / d

        return (xs1, ys1), (xs2, ys2)


# make loop here
# grab things from an actual file, from the f-table to map fuckin you know whats up

x1 = -2.0
x2 = 6.0
x3 = 4.0

y1 = 5.0
y2 = 6.0
y3 = 3.0

a = [x1, y1]
b = [x2, y2]
c = [x3, y3]

A = sqrt(((b[0] - c[0]) ** 2) + ((b[1] - c[1]) ** 2))
B = sqrt(((a[0] - c[0]) ** 2) + ((a[1] - c[1]) ** 2))
C = sqrt(((b[0] - a[0]) ** 2) + ((b[1] - a[1]) ** 2))

longest_side = A if B < A and C < A else B if C < B and A < B else C

radius_one = float()
radius_two = float()
point_one = [float(), float()]
point_two = [float(), float()]

if longest_side == A:
    radius_one, radius_two = B, C
    point_one, point_two = c, b
elif longest_side == B:
    radius_one, radius_two = A, C
    point_one, point_two = c, a
else:
    radius_one, radius_two = A, B
    point_one, point_two = b, a

geom = Geometry()
our_geometry = geom.circle_intersection((point_one[0], point_one[1], radius_one),
                                        (point_two[0], point_two[1], radius_two))

(one, two), (three, four) = our_geometry
origin = (((one + three) / 2), ((two + four) / 2))
print(origin)
