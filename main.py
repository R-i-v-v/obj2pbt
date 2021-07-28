from __future__ import division
from math import sqrt
import utils.constructors as construct
from re import findall


vertices_by_line, maps_by_line = construct.file_splitter('input/gummyRing.obj', 'work/vertex.txt', 'work/map.txt')
print(f'v: {len(vertices_by_line)}; f: {len(maps_by_line)}')
open('output/output.obj', 'w').close()
output_file = open('output/output.obj', 'a')

current_line = 0
for map in maps_by_line:
    a = {"x": float(), "y": float(), "z": float()}  # reset all points
    b = {"x": float(), "y": float(), "z": float()}  # index 0 is x, index 1 is y, index 2 is z
    c = {"x": float(), "y": float(), "z": float()}
    for target_line, point in zip([int(s) for s in findall(r'-?\d+\.?\d*', map)], [a, b, c]):
        for value, index in zip([float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])], ["x", "y", "z"]):
            point[index] = value

    # set lines
    A = sqrt(((b['x'] - c['x']) ** 2) + ((b['y'] - c['y']) ** 2) + ((b['z'] - c['z']) ** 2))
    B = sqrt(((a['x'] - c['x']) ** 2) + ((a['y'] - c['y']) ** 2) + ((a['z'] - c['z']) ** 2))
    C = sqrt(((b['x'] - a['x']) ** 2) + ((b['y'] - a['y']) ** 2) + ((b['z'] - a['z']) ** 2))

    longest_side = A if B < A and C < A else B if C < B and A < B else C

    radius_one = float()
    radius_two = float()
    point_one = {'x': float(), 'y': float(), 'z': float()}
    point_two = {'x': float(), 'y': float(), 'z': float()}
    point_l = {'x': float(), 'y': float(), 'z': float()}

    if longest_side == A:
        radius_one, radius_two = C, B
        point_one, point_two, point_l = b, c, a
    elif longest_side == B:
        radius_one, radius_two = A, C
        point_one, point_two, point_l = c, a, b
    else:
        radius_one, radius_two = A, B
        point_one, point_two, point_l = b, a, c


    our_geometry = construct.circle_intersection((0.0, 0.0, radius_one),
                                                 (longest_side, 0.0, radius_two))

    (one, two), (three, four) = our_geometry
    temp_length = abs((one + three) / 2)
    percent_length = temp_length / longest_side

    xDifference = abs(point_one['x'] - point_two['x'])
    yDifference = abs(point_one['y'] - point_two['y'])
    zDifference = abs(point_one['z'] - point_two['z'])
    origin = {"x": float(), "y": float(), "z": float()}
    if point_one['x'] < point_two['x']:
        origin['x'] = (percent_length * xDifference) + point_one['x']
    elif point_one['x'] > point_two['x']:
        origin['x'] = (percent_length * xDifference) - point_one['x']
    elif point_one['x'] == point_two['x']:
        origin['x'] = point_one['x']

    if point_one['y'] < point_two['y']:
        origin['y'] = (percent_length * yDifference) + point_one['y']
    elif point_one['y'] > point_two['y']:
        origin['y'] = (percent_length * yDifference) - point_one['y']
    elif point_one['y'] == point_two['y']:
        origin['y'] = point_one['y']

    if point_one['z'] < point_two['z']:
        origin['z'] = (percent_length * zDifference) + point_one['z']
    elif point_one['z'] > point_two['z']:
        origin['z'] = (percent_length * zDifference) - point_one['z']
    elif point_one['z'] == point_two['z']:
        origin['z'] = point_one['z']

    output_file.write(f"v {origin['x']} {origin['y']} {origin['z']}\n")
    output_file.write(f"v {point_l['x']} {point_l['y']} {point_l['z']}\n")
    output_file.write(f"v {point_one['x']} {point_one['y']} {point_one['z']}\n")
    output_file.write(f"v {point_two['x']} {point_two['y']} {point_two['z']}\n")
    current_line += 5

    output_file.write(f"f {current_line-4} {current_line-3} {current_line-2}\n")
    output_file.write(f"f {current_line-4} {current_line-3} {current_line-1}\n")
    current_line += 1

    print(f'For the triangle made by map [{map}]...\nThe longest side has length {longest_side}.\nA: {A}, B: {B}, C: {C}\nPoint 1: {point_one}\nPoint 2: {point_two}\nRadius 1: {radius_one}\nRadius 2: {radius_two}\n')
