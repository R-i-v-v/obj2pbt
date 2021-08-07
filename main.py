from __future__ import division
from time import time
from decimal import Decimal
from re import findall
from os import scandir
from json import dumps, loads
import numpy as np
from scipy.spatial.transform import Rotation as R
from generatePBT import PBT

# triangle splitting function courtesy of waffle#3956
# converts three points in 3D space into euler angles that core can handle, in theory
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
    len_0, len_1 = np.linalg.norm(ba), np.linalg.norm(p)
    y, z = np.divide(p, len_1), np.divide(ba, len_0)
    x = np.cross(y, z)
    width_1 = dot * len_0
    width_2 = (1 - dot) * len_0

    position_1 = np.add(
        np.subtract([(c[0] + a[0]) * .5, (c[1] + a[1]) * .5, (c[2] + a[2]) * .5], np.multiply(y, len_1 / 2)),
        np.multiply(z, width_1 / 2))
    position_2 = np.subtract(
        np.subtract([(c[0] + b[0]) * .5, (c[1] + b[1]) * .5, (c[2] + b[2]) * .5], np.multiply(y, len_1 / 2)),
        np.multiply(z, width_2 / 2))
    scale_1, scale_2 = np.divide([width_1, len_1, 0], 100), np.divide([len_1, width_2, 0], 100)
    matrix_1, matrix_2 = np.transpose([z, -y, x]), np.transpose([-y, -z, x])
    if flip:
        matrix_1, matrix_2 = np.transpose([-z, -y, -x]), np.transpose([-y, z, -x])
        scale_1, scale_2 = np.divide([width_2, len_1, 0], 100), np.divide([len_1, width_1, 0], 100)
    rotation_1 = R.from_matrix(matrix_1).as_euler('xyz', degrees=True)*[-1, -1, 1]
    rotation_2 = R.from_matrix(matrix_2).as_euler('xyz', degrees=True)*[-1, -1, 1]
    return (position_1, position_2, scale_1, scale_2, rotation_1, rotation_2)


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
        start_time = time()
        pbt_output = PBT(name='EpicPythonGeneratedTemplate')

        # reset vertex, map, origins, and output if they exist
        # read input and output files into memory
        open('work/vertex.txt', 'w').close(), open('work/map.txt', 'w').close(), open('work/triplets', 'w').close()
        open(f'output/{entry.name[:-4]}.pbt', 'w').close()
        vertex_file, map_file = open('work/vertex.txt', 'a'), open('work/map.txt', 'a')
        input_file, output_file = open(f'input/{entry.name}', 'r'), open(f'output/{entry.name[:-4]}.pbt', 'a')
        input_lines = input_file.readlines()

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
            for position, scale, rotation in zip([position_one, position_two], [scale_one, scale_two], [rotation_one, rotation_two]):
                pbt_output.add_mesh('testMesh', 'sm_cube_002', position, rotation, np.multiply(scale, 10), None)

        output_file.write(pbt_output.generate_pbt())

        output_file.close()
        print(f'<{entry.name}> {len(vertices_by_line)} vertices and {len(face_maps_by_line)} faces')
        print(f'Found {len(open(f"work/origins.obj", "r").readlines())} origins and {len(open(f"work/triplets", "r").readlines())} triangles.\nFinished in {round(Decimal(time() - start_time) * 1000, 3)} ms.\n')