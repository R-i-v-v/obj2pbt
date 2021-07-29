from __future__ import division
from math import sqrt
from re import findall
from os import scandir

with scandir('input') as dirs:
    for entry in dirs:
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
        maps_by_line = [n.strip() for n in open('work/map.txt', 'r').readlines()]
        print(f'Total vertex count: {len(vertices_by_line)}\nTotal f-map count: {len(maps_by_line)}')

        if entry.name == 'input.obj':
            open('output/output.obj', 'w').close()
            output_file = open('output/output.obj', 'a')
        else:
            open(f'output/{entry.name[:-4]}_origins.obj', 'w').close()
            output_file = open(f'output/{entry.name[:-4]}_origins.obj', 'a')

        current_line = 0
        for map in maps_by_line:
            a, b, c = {}, {}, {}  # reset points to empty dicts
            for target_line, point in zip([int(s) for s in findall(r'-?\d+\.?\d*', map)], [a, b, c]):
                for value, index in zip([float(x) for x in findall(r'-?\d+\.?\d*', vertices_by_line[target_line-1])], ["x", "y", "z"]):
                    point[index] = value  # set dict structure to {'x': float(), 'y': float(), 'z': float()}

            # set lines
            AB = sqrt(((a['x'] - b['x']) ** 2) + ((a['y'] - b['y']) ** 2) + ((a['z'] - b['z']) ** 2))
            BC = sqrt(((b['x'] - c['x']) ** 2) + ((b['y'] - c['y']) ** 2) + ((b['z'] - c['z']) ** 2))
            AC = sqrt(((a['x'] - c['x']) ** 2) + ((a['y'] - c['y']) ** 2) + ((a['z'] - c['z']) ** 2))

            longest_side, point_one, point_two, radius_one, radius_two = (AB, b, a, BC, AC) if BC < AB and AC < AB else (BC, c, b, AC, AB) if AC < BC and AB < BC else (AC, c, a, BC, AB)

            h = 1 / 2 + (radius_one ** 2 - radius_two ** 2) / (2 * longest_side ** 2)

            origin = {}
            for coord in ['x', 'y', 'z']:
                origin[coord] = point_one[coord] + h * (point_two[coord] - point_one[coord])

            output_file.write(f"v {origin['x']} {origin['y']} {origin['z']}\n")

            print(f'For the triangle made by map [{map}]...\na — {a}\nb — {b}\nc — {c}\no — {origin}\n')
