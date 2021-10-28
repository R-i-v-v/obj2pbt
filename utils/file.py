from os.path import isabs
from pathlib import Path
from PIL import Image

def readData(path, uuid, parent, pbt_output, entry_name, readTextures):
    vertex_file, map_file, texture_cords_file = open(f'{parent}/{uuid}-vertex.txt', 'a'), open(f'{parent}/{uuid}-map.txt', 'a'), open(f'{parent}/{uuid}-texture.txt', 'a')
    input_file, output_file, mtl_file = open(f'{path}', 'r'), open(f'{parent}/{entry_name}.pbt', 'a'), None
    input_lines = input_file.readlines()
    textures_by_index, textures = {}, {} #textures_by_index corresponds to the mat name of a group, textures is the actual texture data of a texture with the mat name being used as key.

    # extract vertices, face-maps, and groups from input .obj file
    object_number, g_count = 1, 0
    folders, group_names = [], []
    for line in input_lines:
        if line.startswith('v '):
            vertex_file.write(line[2:])
        elif line.startswith('g ') or line.startswith('o '):
            object_number += 1
            g_count += 1
            group_names.append(line[2:].lower().strip())
            folders.append(pbt_output.add_folder(f"{line[2:].title().strip()}"))
        elif line.startswith('vt '):
            texture_cords_file.write(line[3:])
        elif line.startswith('f '):
            map_file.write(f'{line[1:].strip()} {object_number - 1}\n')
        elif line.startswith('mtllib '):
            mtl_file = line[7:-1]
        elif line.startswith('usemtl '):
            textures_by_index[g_count - 1] = line[7:]

    if g_count == 0:
        folders.append(pbt_output.add_folder(f"Model"))
    vertex_file.close(), map_file.close(), texture_cords_file.close()

    # get vertices and face-maps by line
    vertices_by_line = [n.strip() for n in open(f'{parent}/{uuid}-vertex.txt', 'r').readlines()]
    face_maps_by_line = [n.strip() for n in open(f'{parent}/{uuid}-map.txt', 'r').readlines()]
    texture_cords_by_line = [n.strip() for n in open(f'{parent}/{uuid}-texture.txt', 'r').readlines()]

    if mtl_file is not None and readTextures:
        mtl_raw_data = open(f'{parent}/{mtl_file}')
        mat_name = ""
        for line in mtl_raw_data.readlines():
            if line.startswith('newmtl '):
                mat_name = line[7:]
                textures[mat_name] = {}
            elif line.startswith('map_Kd '):
                if len(line[7:-1]) > 1:
                    path = line[7:-1]
                    if not isabs(path): #If the path isn't absolute it changes path to absolute
                        path = Path(f'{parent}/{line[7:-1]}')
                    texture = Image.open(path)
                    textures[mat_name][0] = texture
            elif line.startswith('Kd'):
                textures[mat_name][1] = [float(n) for n in line[3:].split()]

    return (vertices_by_line, face_maps_by_line, texture_cords_by_line, textures_by_index, textures, folders, group_names, output_file, input_file, g_count)

