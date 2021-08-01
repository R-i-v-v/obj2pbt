from __future__ import division
from time import time
from decimal import Decimal
from math import sqrt
from re import findall
from os import scandir

with scandir('input') as dirs:
    for entry in dirs:
        start_time = time()
        open('work/vertex.txt', 'w').close()
        open('work/map.txt', 'w').close()
        vertex_file = open('work/vertex.txt', 'a')
        map_file = open('work/map.txt', 'a')
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

        if entry.name == 'input.obj':
            open('output/output.obj', 'w').close()
            output_file = open('output/output.obj', 'a')
        else:
            open(f'output/{entry.name[:-4]}_origins.obj', 'w').close()
            output_file = open(f'output/{entry.name[:-4]}_origins.obj', 'a')

        current_line = 0
        for triangle_map in face_maps_by_line:
            a, b, c = {}, {}, {}  # reset points to empty dicts
            for target_line, point in zip([int(x.split('/')[0] if '/' in x else x) for x in [s for s in findall(r'-?\d+\.?\d*/?\d*/?\d*', triangle_map)]], [a, b, c]):
                for value, index in zip([float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])], ["x", "y", "z"]):
                    point[index] = value

            # set lines
            AB = sqrt(((a['x'] - b['x']) ** 2) + ((a['y'] - b['y']) ** 2) + ((a['z'] - b['z']) ** 2))
            BC = sqrt(((b['x'] - c['x']) ** 2) + ((b['y'] - c['y']) ** 2) + ((b['z'] - c['z']) ** 2))
            AC = sqrt(((a['x'] - c['x']) ** 2) + ((a['y'] - c['y']) ** 2) + ((a['z'] - c['z']) ** 2))

            if max(AB ** 2, BC ** 2, AC ** 2) == (AB ** 2 + BC ** 2 + AC ** 2 - max(AB ** 2, BC ** 2, AC ** 2)):
                continue

            longest_side, point_one, point_two, radius_one, radius_two = (AB, b, a, BC, AC) if BC < AB and AC < AB else (BC, c, b, AC, AB) if AC < BC and AB < BC else (AC, c, a, BC, AB)

            h = 1 / 2 + (radius_one ** 2 - radius_two ** 2) / (2 * longest_side ** 2)

            origin = {}
            for coord in ['x', 'y', 'z']:
                origin[coord] = point_one[coord] + h * (point_two[coord] - point_one[coord])

            output_file.write(f"v {origin['x']} {origin['y']} {origin['z']}\n")

        output_file.close()
        output_string = f'{"output" if entry.name[:-4] == "input" else entry.name[:-4]}{"" if entry.name[:-4] == "input" else "_origins"}'
        print(f'Finished finding {len(open(f"output/{output_string}.obj", "r").readlines())} origins in {round(Decimal(time()-start_time)*1000,3)} ms.\n')