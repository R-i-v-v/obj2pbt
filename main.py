from __future__ import division
from time import time
from decimal import Decimal
from re import findall
from os import scandir
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
    return position_1, position_2, scale_1, scale_2, rotation_1, rotation_2


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
        pbt_output = PBT(name=f'{entry.name[:-4]}')

        # reset vertex, map, and output if they exist
        # read input and output files into memory
        open('work/vertex.txt', 'w').close(), open('work/map.txt', 'w').close()
        open(f'output/{entry.name[:-4]}.pbt', 'w').close()
        vertex_file, map_file = open('work/vertex.txt', 'a'), open('work/map.txt', 'a')
        input_file, output_file = open(f'input/{entry.name}', 'r'), open(f'output/{entry.name[:-4]}.pbt', 'a')
        input_lines = input_file.readlines()

        # extract vertices, face-maps, and groups from input .obj file
        object_number, g_count = 1, 0
        merged_models = []
        for line in input_lines:
            if line.startswith('v '):
                vertex_file.write(line[2:])
            elif line.startswith('g '):
                object_number += 1
                g_count += 1
                merged_models.append(pbt_output.add_merged_model())
            elif line.startswith('f '):
                map_file.write(f'{line[1:].strip()} {object_number-1}\n')
        if g_count == 0:
            merged_models.append(pbt_output.add_merged_model())
        vertex_file.close(), map_file.close()

        # get vertices by line
        vertices_by_line = [n.strip() for n in open('work/vertex.txt', 'r').readlines()]
        face_maps_by_line = [n.strip() for n in open('work/map.txt', 'r').readlines()]

        for triangle_map in face_maps_by_line:  # iterate through each face map
            a, b, c = [], [], []  # reset vectors to empty lists
            maps_gs = [s for s in findall(r'-?\d+\.?\d*/?\d*/?\d*', triangle_map)]
            for target_line, point in zip([int(x.split('/')[0] if '/' in x else x) for x in maps_gs[:3]], [a, b, c]):
                for value in [float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])]:
                    point.append(value)
            group = 0 if int(maps_gs[3]) == 0 else int(maps_gs[3]) - 1
            core_a = [a[2], a[0], a[1]]
            core_b = [b[2], b[0], b[1]]
            core_c = [c[2], c[0], c[1]]
            position_one, position_two, scale_one, scale_two, rotation_one, rotation_two = triangle(core_a, core_b, core_c)
            for position, scale, rotation in zip([position_one, position_two], [scale_one, scale_two], [rotation_one, rotation_two]):
                if position is not None and scale is not None and rotation is not None:
                    if scale[2] == 0:
                        scale[0], scale[1], scale[2] = 0.0002, scale[0], scale[1]
                        # scale[2] = 0.001
                    rotation[0] -= 90
                    rotation[1] -= 90
                    # rotation[2] += 5
                    merged_models[group].add_child('testMesh', "sm_wedge_002", np.multiply(position, 10), rotation, np.multiply(scale, 10), None)
                else:
                    continue


        output_file.write(pbt_output.generate_pbt())

        input_file.close(), output_file.close()
        print(f'<{entry.name}> {len(vertices_by_line)} vertices and {len(face_maps_by_line)} faces')
        print(f'Finished in {round(Decimal(time() - start_time) * 1000, 3)} ms.\n')