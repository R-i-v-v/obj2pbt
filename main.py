from __future__ import division
from time import time
from decimal import Decimal
from math import sqrt
from re import findall
from os import scandir
from json import dumps


def set_dict(o, point, opposite, file):
    output = {
        'o': {  # origin point
            'x': o['x'],
            'y': o['y'],
            'z': o['z']
        },
        'a': {  # one of longest_side's endpoints
            'x': point['x'],
            'y': point['y'],
            'z': point['z']
        },
        'b': {  # point opposite the origin
            'x': opposite['x'],
            'y': opposite['y'],
            'z': opposite['z']
        }
    }
    file.write(f'{dumps(output)}\n')

with scandir('input') as dirs:
    for entry in dirs:
        start_time, rights_count = time(), 0
        open('work/vertex.txt', 'w').close()
        open('work/map.txt', 'w').close()
        open('work/origins.obj', 'w').close()
        vertex_file = open('work/vertex.txt', 'a')
        map_file = open('work/map.txt', 'a')
        obj_file = open('work/origins.obj', 'a')
        input_file = open(f'input/{entry.name}', 'r')
        input_lines = input_file.readlines()
        for line in input_lines:
            if line.startswith('v '):
                vertex_file.write(line[2:])
            elif line.startswith('f '):
                map_file.write(line[2:])

        vertex_file.close()
        map_file.close()

        vertices_by_line = [n.strip() for n in open('work/vertex.txt', 'r').readlines()]
        face_maps_by_line = [n.strip() for n in open('work/map.txt', 'r').readlines()]
        print(f'<{entry.name}> {len(vertices_by_line)} vertices and {len(face_maps_by_line)} faces')

        open(f'output/{entry.name[:-4]}', 'w').close()
        output_file = open(f'output/{entry.name[:-4]}', 'a')

        current_line = 0
        for triangle_map in face_maps_by_line:  # iterate through each f-map line
            a, b, c = {}, {}, {}  # reset points to empty dicts
            for target_line, point in zip([int(x.split('/')[0] if '/' in x else x) for x in [s for s in findall(r'-?\d+\.?\d*/?\d*/?\d*', triangle_map)]], [a, b, c]):
                for value, index in zip([float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])], ["x", "y", "z"]):
                    point[index] = value

            # get vectors AB, AC, and BC.
            ab_v = {'x': a['x'] - b['x'], 'y': a['y'] - b['y'], 'z': a['z'] - b['z']}
            ac_v = {'x': a['x'] - c['x'], 'y': a['y'] - c['y'], 'z': a['z'] - c['z']}
            bc_v = {'x': b['x'] - c['x'], 'y': b['y'] - c['y'], 'z': b['z'] - c['z']}

            # calculate lengths of AB, AC, and BC by squaring vectors
            AB = sqrt((ab_v['x'] ** 2) + (ab_v['y'] ** 2) + (ab_v['z'] ** 2))
            AC = sqrt((ac_v['x'] ** 2) + (ac_v['y'] ** 2) + (ac_v['z'] ** 2))
            BC = sqrt((bc_v['x'] ** 2) + (bc_v['y'] ** 2) + (bc_v['z'] ** 2))

            # if right triangle, write vertex corresponding to pi/2 radians to output file
            if max(AB ** 2, BC ** 2, AC ** 2) == (AB ** 2 + BC ** 2 + AC ** 2 - max(AB ** 2, BC ** 2, AC ** 2)):
                rights_count += 1
                flip = {}
                if (ab_v['x'] * ac_v['x']) + (ab_v['y'] * ac_v['y']) + (ab_v['z'] * ac_v['z']) == 0:
                    flip = a  # if AB/AC orthogonal, origin is a
                elif (ab_v['x'] * bc_v['x']) + (ab_v['y'] * bc_v['y']) + (ab_v['z'] * bc_v['z']) == 0:
                    flip = b  # if AB/BC orthogonal, origin is b
                else:
                    flip = c  # AC/BC must be orthogonal, thus origin is c
                obj_file.write(f"v {flip['x']} {flip['y']} {flip['z']}\n")
                set_dict({'x': flip['x'], 'y': flip['y'], 'z': flip['z']},
                         b if flip == a else c if flip == b else a,
                         c if flip == a else a if flip == b else b,
                         output_file)
                continue  # move on and start from the top with the next triangle

            # we need to get the longest side, as well as the two points it falls in between
            # we need to use the two other sides as sphere radii
            longest_side, point_one, point_two, point_three, radius_one, radius_two = (AB, b, a, c, BC, AC) if BC < AB and AC < AB else (BC, c, b, a, AC, AB) if AC < BC and AB < BC else (AC, c, a, b, BC, AB)

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

        obj_file.close()
        output_file.close()
        print(f'Found {len(open(f"work/origins.obj", "r").readlines())} origins and {len(open(f"output/{entry.name[:-4]}", "r").readlines())} triangles.\n{rights_count} right triangles.\nFinished in {round(Decimal(time()-start_time)*1000,3)} ms.\n')