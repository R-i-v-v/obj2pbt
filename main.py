from __future__ import division
from math import sqrt
import utils.constructors as construct


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

our_geometry = construct.circle_intersection((point_one[0], point_one[1], radius_one),
                                             (point_two[0], point_two[1], radius_two))

(one, two), (three, four) = our_geometry
origin = (((one + three) / 2), ((two + four) / 2))
print(origin)


construct.file_splitter('input/input.obj', 'output/vertex.txt', 'output/map.txt')