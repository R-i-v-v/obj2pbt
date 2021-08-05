from __future__ import division
from time import time
from decimal import Decimal
from math import sin, cos, asin, acos, atan2, sqrt, pi, degrees as d
from re import findall
from os import scandir
from json import dumps, loads
import numpy as np

b'''

2- how the hell does that point triplet to euler angles even WORK!?
3- do we need to swap values due to the fact that cinema4d and core handle depth and height differently?

'''


def normalize(v):
    return v / np.linalg.norm(v)


def quaternion_to_euler(q):
    x, y, z, w = q[0], q[1], q[2], q[3]
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = atan2(t0, t1)
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = asin(t2)
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = atan2(t3, t4)
    return [roll, pitch, yaw]


def vectors_to_quaternion(v):
    v_oa, v_ob = v[0], v[1]
    oa_x_ob, oa_d_ob = np.cross(v_oa, v_ob), np.dot(v_oa, v_ob)

    mag_of_v_oa, mag_of_v_ob = sqrt(v_oa[0] ** 2 + v_oa[1] ** 2 + v_oa[2] ** 2), sqrt(v_ob[0] ** 2 + v_ob[1] ** 2 + v_ob[2] ** 2)
    theta = acos(oa_d_ob / (mag_of_v_oa * mag_of_v_ob))
    oa_x_ob_norm = normalize(oa_x_ob)

    q1 = oa_x_ob_norm[0] * sin(theta / 2)
    q2 = oa_x_ob_norm[1] * sin(theta / 2)
    q3 = oa_x_ob_norm[2] * sin(theta / 2)
    q4 = cos(theta / 2)

    return [q1, q2, q3, q4]


def points_to_vectors(o, a, b):
    v_oa, v_ob = np.subtract(a, o), np.subtract(b, o)
    return [v_oa, v_ob]


def set_dict(origin, point, polar, file):
    output = {
        'o': origin,  # origin point and scale factors
        'a': point,  # one of longest_side's endpoints
        'b': polar,  # point opposite the origin
    }
    file.write(f'{dumps(output)}\n')


def find_right_angle(a, b, c):
    v_ab, v_ac, v_bc = np.subtract(b, a), np.subtract(c, a), np.subtract(c, b)
    if -0.001 < np.dot(v_ab, v_ac) < 0.001:
        return a
    elif -0.001 < np.dot(v_ab, v_bc) < 0.001:
        return b
    elif -0.001 < np.dot(v_ac, v_bc) < 0.001:
        return c
    else:
        return None

# identity matrix
I = [[1, 0, 0],
     [0, 1, 0],
     [0, 0, 1]]

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

        for triangle_map in face_maps_by_line:  # iterate through each f-map line
            a, b, c = [], [], []  # reset points to empty dicts
            for target_line, point in zip([int(x.split('/')[0] if '/' in x else x) for x in [s for s in findall(r'-?\d+\.?\d*/?\d*/?\d*', triangle_map)]], [a, b, c]):
                for value in [float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])]:
                    point.append(value)

            # if right triangle, write vertex corresponding to pi/2 radians to output file
            right_check = find_right_angle(a, b, c)
            if right_check:
                rights_count += 1
                obj_file.write(f"v {right_check[0]} {right_check[1]} {right_check[2]}\n")
                set_dict(right_check,
                         b if right_check == a else c if right_check == b else a,
                         c if right_check == a else a if right_check == b else b,
                         triplets)
                continue

            # get vectors AB, AC, and BC
            ab_v, ac_v, bc_v = np.subtract(a, b), np.subtract(a, c), np.subtract(b, c)

            # calculate lengths AB, AC, and BC by squaring vectors and taking the root of their sum
            ab_l, ac_l, bc_l = np.sqrt(ab_v.dot(ab_v)), np.sqrt(ac_v.dot(ac_v)), np.sqrt(bc_v.dot(bc_v))

            # get the longest side, as well as the two points it falls in between
            # get the point opposite the longest side and use other two sides as sphere radii
            longest_side, point_one, point_two, point_three, radius_one, radius_two = (ab_l, b, a, c, bc_l, ac_l) if bc_l < ab_l and ac_l < ab_l else (bc_l, c, b, a, ac_l, ab_l) if ac_l < bc_l and ab_l < bc_l else (ac_l, c, a, b, bc_l, ab_l)

            # i don't know what h represents, but it's required for the intersection equation below.
            h = 1 / 2 + (radius_one ** 2 - radius_two ** 2) / (2 * longest_side ** 2)

            # compute the x, y, and z coordinates of the point that lies at the center of
            # the circle of intersection between two spheres of aforementioned radii
            origin = []
            for coord in range(3):
                origin.append(point_one[coord] + h * (point_two[coord] - point_one[coord]))
            obj_file.write(f"v {origin[0]} {origin[1]} {origin[2]}\n")

            # split up triangle into two ALLEGEDLY right triangles
            # add each right triangle as two lines in triplets file
            for point in [point_one, point_two]:
                split_check = find_right_angle(origin, point, point_three)
                if split_check:
                    set_dict(origin, point, point_three, triplets)
                else:
                    exit()


        triplets.close()
        triplets_by_line = [n.strip() for n in open('work/triplets', 'r').readlines()]
        for line in triplets_by_line:
            triplet = loads(line)
            o, a, b = triplet['o'], triplet['a'], triplet['b']
            # print([d(n) for n in quaternion_to_euler(vectors_to_quaternion(points_to_vectors(o, a, b)))])
            print(quaternion_to_euler(vectors_to_quaternion(points_to_vectors(o, a, b))))

        obj_file.close(), triplets.close()
        print(f'<{entry.name}> {len(vertices_by_line)} vertices and {len(face_maps_by_line)} faces')
        print(f'Found {len(open(f"work/origins.obj", "r").readlines())} origins and {len(open(f"work/triplets", "r").readlines())} triangles.\n{rights_count} right triangles.\nFinished in {round(Decimal(time() - start_time) * 1000, 3)} ms.\n')
        output_file.close()