from __future__ import division
from time import time
from decimal import Decimal
from re import findall
from os import scandir
from json import dumps, loads
import numpy as np
from scipy.spatial.transform import Rotation as R


def triangle(a, b, c):
    ba, ca = np.subtract(b, a), np.subtract(c, a)
    dot = np.dot(ba, ca)
    flip = False
    if dot > 0:
        if dot >= np.dot(ba, ba):
            b, c, ba, ca = c, b, ca, ba
        else:
            flip = True
    else:
        a, c = c, a
        ba, ca = np.subtract(b, a), np.negative(ca)
        dot = np.dot(ba, ca)
    dot /= ba.dot(ba)
    p = np.subtract(ca, np.multiply(ba, dot))
    len0, len1 = np.linalg.norm(ba), np.linalg.norm(p)
    y, z = np.divide(p, len1), np.divide(ba, len0)
    x = np.cross(y, z)
    width1 = dot * len0
    width2 = (1 - dot) * len0

    position1 = np.add(
        np.subtract([(c[0] + a[0]) * .5, (c[1] + a[1]) * .5, (c[2] + a[2]) * .5], np.multiply(y, len1 / 2)),
        np.multiply(z, width1 / 2))
    position2 = np.subtract(
        np.subtract([(c[0] + b[0]) * .5, (c[1] + b[1]) * .5, (c[2] + b[2]) * .5], np.multiply(y, len1 / 2)),
        np.multiply(z, width2 / 2))
    scale1 = np.divide([width1, len1, 0], 100)
    scale2 = np.divide([len1, width2, 0], 100)
    matrix1 = np.transpose([z, -y, x])
    matrix2 = np.transpose([-y, -z, x])
    if flip:
        matrix1 = np.transpose([-z, -y, -x])
        matrix2 = np.transpose([-y, z, -x])
        scale1 = np.divide([width2, len1, 0], 100)
        scale2 = np.divide([len1, width1, 0], 100)
    rotation1 = R.from_matrix(matrix1).as_euler('xyz', degrees=True)*[-1, -1, 1]
    rotation2 = R.from_matrix(matrix2).as_euler('xyz', degrees=True)*[-1, -1, 1]
    return [position1, position2, scale1, scale2, rotation1, rotation2]


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

np.set_printoptions(16)

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

            position_one, position_two, scale_one, scale_two, rotation_one, rotation_two = triangle(a, b, c)
            o_dict = {
                'one': {
                    'pos': list(position_one),
                    'scale': list(np.multiply(scale_one, 10)),
                    'rot': list(rotation_one)
                },
                'two': {
                    'pos': list(position_two),
                    'scale': list(np.multiply(scale_two, 10)),
                    'rot': list(rotation_two)
                }
            }
            triplets.write(f'{dumps(o_dict)}\n')

        obj_file.close(), triplets.close()
        print(f'<{entry.name}> {len(vertices_by_line)} vertices and {len(face_maps_by_line)} faces')
        print(f'Found {len(open(f"work/origins.obj", "r").readlines())} origins and {len(open(f"work/triplets", "r").readlines())} triangles.\n{rights_count} right triangles.\nFinished in {round(Decimal(time() - start_time) * 1000, 3)} ms.\n')
        output_file.close()
