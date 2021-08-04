from __future__ import division
from time import time
from decimal import Decimal
from math import sqrt, atan, degrees as d
from re import findall
from os import scandir
from json import dumps, loads
import numpy as np


b'''

2- how the hell does that point triplet to euler angles even WORK!?
3- do we need to swap values due to the fact that cinema4d and core handle depth and height differently?

'''

# identity matrix
I = [[1, 0, 0],
     [0, 1, 0],
     [0, 0, 1]]

def set_dict(origin, point, polar, file):
    output = {
        'o': origin,  # origin point and scale factors
        'a': point,  # one of longest_side's endpoints
        'b': polar,  # point opposite the origin
    }
    file.write(f'{dumps(output)}\n')


# iterate through files in input directory
with scandir('input') as dirs:
    for entry in dirs:
        start_time, rights_count = time(), 0

        # reset vertex, map, origins, and output if they exist
        # read input and output files into memory
        open('work/vertex.txt', 'w').close(), open('work/map.txt', 'w').close(), open('work/triplets', 'w').close()
        open('work/origins.obj', 'w').close(), open(f'output/{entry.name[:-4]}.pbt', 'w').close()
        vertex_file = open('work/vertex.txt', 'a')
        map_file = open('work/map.txt', 'a')
        triplets = open('work/triplets', 'a')
        obj_file = open('work/origins.obj', 'a')
        input_file = open(f'input/{entry.name}', 'r')
        input_lines = input_file.readlines()
        output_file = open(f'output/{entry.name[:-4]}.pbt', 'a')

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

            # make dicts for vectors AB, AC, and BC
            ab_v = [a['x'] - b['x'], a['y'] - b['y'], a['z'] - b['z']]
            ac_v = [a['x'] - c['x'], a['y'] - c['y'], a['z'] - c['z']]
            bc_v = [b['x'] - c['x'], b['y'] - c['y'], b['z'] - c['z']]

            # calculate lengths AB, AC, and BC by squaring vectors and taking the root of their sum
            ab_l = sqrt((ab_v[0] ** 2) + (ab_v[1] ** 2) + (ab_v[2] ** 2))
            ac_l = sqrt((ac_v[0] ** 2) + (ac_v[1] ** 2) + (ac_v[2] ** 2))
            bc_l = sqrt((bc_v[0] ** 2) + (bc_v[1] ** 2) + (bc_v[2] ** 2))

            # if right triangle, write vertex corresponding to pi/2 radians to output file
            if max(ab_l ** 2,
                   bc_l ** 2,
                   ac_l ** 2) == (ab_l ** 2 + bc_l ** 2 + ac_l ** 2 - max(ab_l ** 2,
                                                                          bc_l ** 2,
                                                                          ac_l ** 2)):
                rights_count += 1
                flip = {}  # dot products checking if vectors orthogonal
                flip = a if not np.dot(ab_v, ac_v) else b if not np.dot(ab_v, bc_v) else c
                obj_file.write(f"v {flip['x']} {flip['y']} {flip['z']}\n")
                set_dict(flip,
                         b if flip == a else c if flip == b else a,
                         c if flip == a else a if flip == b else b,
                         triplets)
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
                set_dict(origin, point, point_three, triplets)

        obj_file.close(), triplets.close()
        print(f'Found {len(open(f"work/origins.obj", "r").readlines())} origins and {len(open(f"work/triplets", "r").readlines())} triangles.\n{rights_count} right triangles.\nFinished in {round(Decimal(time()-start_time)*1000,3)} ms.\n')

        triplets_by_line = [n.strip() for n in open('work/triplets', 'r').readlines()]
        for line in triplets_by_line:
            triplet = loads(line)
            o = [n for n in triplet['o'].values()]
            a, b = [n for n in triplet['a'].values()], [n for n in triplet['b'].values()]
            v_ao, v_ab = np.subtract(o, a), np.subtract(o, b)
            ao_x_ab, ao_c_ab = np.cross(v_ao, v_ab), np.dot(v_ao, v_ab)

            # skew-symmetric cross-product matrix of v
            v_x = [[0, -ao_x_ab[2], ao_x_ab[1]],
                   [ao_x_ab[2], 0, -ao_x_ab[0]],
                   [-ao_x_ab[1], ao_x_ab[0], 0]]

            # v_x ^ 2
            v_x_2 = [[0, -ao_x_ab[2] ** 2, ao_x_ab[1] ** 2],
                     [ao_x_ab[2] ** 2, 0, -ao_x_ab[0] ** 2],
                     [-ao_x_ab[1] ** 2, ao_x_ab[0] ** 2, 0]]

            # calculates last matrix with v_x_2
            for row in v_x_2:
                for item in row:
                    item = item * (1 / (1 + ao_c_ab))

            # adds all three together
            R = [[0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]]
            for x in range(3):
                for y in range(3):
                    R[x][y] = I[x][y] + v_x[x][y] + v_x_2[x][y]

            # angles (in radians)
            # NOTE: not finished. need to do comparisions of numerators and denominators
            alpha = atan(R[1][0] / R[0][0])
            beta = atan(-R[2][0] / sqrt((R[2][1] ** 2) + (R[2][2] ** 2)))
            gamma = atan(R[2][1] / R[2][2])
            print(f'{d(alpha)}, {d(beta)}, {d(gamma)}')
        output_file.close()