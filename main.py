from __future__ import division
from time import time
from decimal import Decimal
from math import sqrt
from re import findall
from os import scandir
from json import dumps


b'''

1- does it matter which of the scaling factors is negative? if so, how do i determine that?
2- how the hell does that point triplet to euler angles even WORK!?
3- do we need to swap values due to the fact that cinema4d and core handle depth and height differently?
4- does set_dict() have to be THAT fat?
 
'''


def set_dict(o, point, opposite, file):
    output = {
        'o': {'x': o['x'] * 10, 'y': o['y'] * 10, 'z': o['z'] * 10},  # origin point and scale factors
        'a_o': sqrt((point['x'] - o['x']) ** 2 + (point['y'] - o['y']) ** 2 + (point['z'] - o['z']) ** 2) / 10,
        'b_o': sqrt((opposite['x'] - o['x']) ** 2 + (opposite['y'] - o['y']) ** 2 + (opposite['z'] - o['z']) ** 2) / 10,
        'a': {'x': point['x'] * 10, 'y': point['y'] * 10, 'z': point['z'] * 10},  # one of longest_side's endpoints
        'b': {'x': opposite['x'] * 10, 'y': opposite['y'] * 10, 'z': opposite['z'] * 10}  # point opposite the origin
    }
    file.write(f'{dumps(output)}\n')


# iterate through files in input directory
with scandir('input') as dirs:
    for entry in dirs:
        start_time, rights_count = time(), 0

        # reset vertex, map, origins, and output if they exist
        # read input and output files into memory
        open('work/vertex.txt', 'w').close(), open('work/map.txt', 'w').close()
        open('work/origins.obj', 'w').close(), open(f'output/{entry.name[:-4]}', 'w').close()
        vertex_file = open('work/vertex.txt', 'a')
        map_file = open('work/map.txt', 'a')
        obj_file = open('work/origins.obj', 'a')
        input_file = open(f'input/{entry.name}', 'r')
        input_lines = input_file.readlines()
        output_file = open(f'output/{entry.name[:-4]}', 'a')

        # extract vertices and faces from input .obj file
        for line in input_lines:
            if line.startswith('v '):
                vertex_file.write(line[2:])
            elif line.startswith('f '):
                map_file.write(line[2:])
        vertex_file.close(), map_file.close()

        # get vertices by line
        vertices_by_line = [n.strip() for n in open('work/vertex.txt', 'r').readlines()]
        face_maps_by_line = [n.strip() for n in open('work/map.txt', 'r').readlines()]
        print(f'<{entry.name}> {len(vertices_by_line)} vertices and {len(face_maps_by_line)} faces')

        for triangle_map in face_maps_by_line:  # iterate through each f-map line
            a, b, c = {}, {}, {}  # reset points to empty dicts
            for target_line, point in zip([int(x.split('/')[0] if '/' in x else x) for x in [s for s in findall(r'-?\d+\.?\d*/?\d*/?\d*', triangle_map)]], [a, b, c]):
                for value, index in zip([float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])], ["x", "y", "z"]):
                    point[index] = value

            # get vectors AB, AC, and BC
            ab_v = {'x': a['x'] - b['x'], 'y': a['y'] - b['y'], 'z': a['z'] - b['z']}
            ac_v = {'x': a['x'] - c['x'], 'y': a['y'] - c['y'], 'z': a['z'] - c['z']}
            bc_v = {'x': b['x'] - c['x'], 'y': b['y'] - c['y'], 'z': b['z'] - c['z']}

            # calculate lengths AB, AC, and BC by squaring vectors and taking the root of their sum
            ab_l = sqrt((ab_v['x'] ** 2) + (ab_v['y'] ** 2) + (ab_v['z'] ** 2))
            ac_l = sqrt((ac_v['x'] ** 2) + (ac_v['y'] ** 2) + (ac_v['z'] ** 2))
            bc_l = sqrt((bc_v['x'] ** 2) + (bc_v['y'] ** 2) + (bc_v['z'] ** 2))

            # if right triangle, write vertex corresponding to pi/2 radians to output file
            if max(ab_l ** 2,
                   bc_l ** 2,
                   ac_l ** 2) == (ab_l ** 2 + bc_l ** 2 + ac_l ** 2 - max(ab_l ** 2,
                                                                          bc_l ** 2,
                                                                          ac_l ** 2)):
                rights_count += 1
                flip = {}  # what the hell even ARE dot products, anyway??
                if (ab_v['x'] * ac_v['x']) + (ab_v['y'] * ac_v['y']) + (ab_v['z'] * ac_v['z']) == 0:
                    flip = a  # if vectors AB and AC are orthogonal, origin is a
                elif (ab_v['x'] * bc_v['x']) + (ab_v['y'] * bc_v['y']) + (ab_v['z'] * bc_v['z']) == 0:
                    flip = b  # if vectors AB and BC are orthogonal, origin is b
                else:
                    flip = c  # vectors AC and BC must be orthogonal, thus origin is c
                obj_file.write(f"v {flip['x']} {flip['y']} {flip['z']}\n")
                set_dict(flip,
                         b if flip == a else c if flip == b else a,
                         c if flip == a else a if flip == b else b,
                         output_file)
                continue  # move on and start from the top with the next triangle

            # get the longest side, as well as the two points it falls in between
            # get the point opposite the longest side and use other two sides as sphere radii
            longest_side, point_one, point_two, point_three, radius_one, radius_two = (ab_l, b, a, c, bc_l, ac_l) if bc_l < ab_l and ac_l < ab_l else (bc_l, c, b, a, ac_l, ab_l) if ac_l < bc_l and ab_l < bc_l else (ac_l, c, a, b, bc_l, ab_l)

            # i don't know what h represents, but it's required for the intersection equation below.
            h = 1 / 2 + (radius_one ** 2 - radius_two ** 2) / (2 * longest_side ** 2)

            # compute the x, y, and z coordinates of the point that lies at the center of
            # the circle of intersection between two spheres of aforementioned radii
            origin = {}
            for coord in ['x', 'y', 'z']:
                origin[coord] = point_one[coord] + h * (point_two[coord] - point_one[coord])
            obj_file.write(f"v {origin['x']} {origin['y']} {origin['z']}\n")

            for point in [point_one, point_two]:
                set_dict(origin, point, point_three, output_file)

        obj_file.close(), output_file.close()
        print(f'Found {len(open(f"work/origins.obj", "r").readlines())} origins and {len(open(f"output/{entry.name[:-4]}", "r").readlines())} triangles.\n{rights_count} right triangles.\nFinished in {round(Decimal(time()-start_time)*1000,3)} ms.\n')