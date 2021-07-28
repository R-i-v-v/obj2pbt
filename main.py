from __future__ import division
from math import sqrt
import utils.constructors as construct
from re import findall


vertices_by_line, maps_by_line = construct.file_splitter('input/input.obj', 'output/vertex.txt', 'output/map.txt')
for map in maps_by_line:
    a = [float(), float(), float()]  # reset all points
    b = [float(), float(), float()]  # index 0 is x, index 1 is y, index 2 is z
    c = [float(), float(), float()]
    for target_line, point in zip([int(s) for s in findall(r'-?\d+\.?\d*', map)], [a, b, c]):
        for value, index in zip([float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])], [0, 1, 2]):
            point[index] = value

    # set lines
    A = sqrt(((b[0] - c[0]) ** 2) + ((b[1] - c[1]) ** 2) + ((b[2] - c[2]) ** 2))
    B = sqrt(((a[0] - c[0]) ** 2) + ((a[1] - c[1]) ** 2) + ((a[2] - c[2]) ** 2))
    C = sqrt(((b[0] - a[0]) ** 2) + ((b[1] - a[1]) ** 2) + ((b[2] - a[2]) ** 2))

    longest_side = A if B < A and C < A else B if C < B and A < B else C

    radius_one = float()
    radius_two = float()
    point_one = [float(), float(), float()]
    point_two = [float(), float(), float()]

    if longest_side == A:
        radius_one, radius_two = B, C
        point_one, point_two = c, b
        tp_one, tp_two = 0.0, longest_side
        tp_one_r, tp_two_r = B, C
    elif longest_side == B:
        radius_one, radius_two = A, C
        point_one, point_two = c, a
        tp_one, tp_two = 0.0, longest_side
        tp_one_r, tp_two_r = A, C
    else:
        radius_one, radius_two = A, B
        point_one, point_two = b, a
        tp_one, tp_two = 0.0, longest_side
        tp_one_r, tp_two_r = A, B


    print(f'For the triangle made by map [{map}]...\nThe longest side has length {longest_side}.\nA: {A}, B: {B}, C: {C}\nPoint 1: {point_one}\nPoint 2: {point_two}\nRadius 1: {radius_one}\nRadius 2: {radius_two}')

    our_geometry = construct.circle_intersection((tp_one, 0.0, tp_one_r),
                                                 (tp_two, 0.0, tp_two_r))

    (one, two), (three, four) = our_geometry
    origin = (((one + three) / 2), ((two + four) / 2))
    print(f'Origin: {origin}\n')