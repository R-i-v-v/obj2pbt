from __future__ import division
from re import findall
from os import remove
from os.path import splitext, isabs
from pathlib import Path, PurePath
import tkinter as tk
from tkinter import filedialog, ttk
import ctypes
import numpy as np
from uuid import uuid4
from PIL import Image
from math import floor

from pbtGenerator import PBT
from b64Image import icon_in_base_64
from triangle import triangle
from applicationGUI import AppUI

# program headed by Rivvnik#1111
np.set_printoptions(16)
myappid = u'mycompany.myproduct.subproduct.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = None  # set taskbar icon

def open_file():
    global file_path, pure_path
    file_path = filedialog.askopenfilename()
    path_name = PurePath(file_path).name
    if len(path_name[:-4]) > 16:
        path_name = path_name[:12] + '...' + path_name[-7:]
    app.aesthetic_path.set(f"{path_name}")


def convert_file():
    global file_path
    if not file_path == '':
        app.root.withdraw()
        run(file_path)
    else:
        open_file()

app = AppUI()
app.ui_init(icon_in_base_64, convert_file, open_file)
app.buttonize()



def run(path):
    entry_name = str(Path(splitext(path)[0])).split('\\')[-1:][0]
    parent = str(Path(path).parent)
    pbt_output = PBT(name=f'{entry_name}')

    # reset vertex, map, and output if they exist
    # read input and output files into memory
    uuid = str(uuid4()).split('-')[-1:][0]
    open(f'{parent}/{uuid}-vertex.txt', 'w').close()
    open(f'{parent}/{uuid}-map.txt', 'w').close()
    open(f'{parent}/{entry_name}.pbt', 'w').close()
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

    if mtl_file is not None and app.texturize.get() == 1:
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

    app.input_btn.place_forget()
    app.input_lbl.place_forget()
    app.convert_btn.place_forget()
    app.optimize_box.place_forget()
    app.texturize_box.place_forget()
    app.root.deiconify()
    app.root.geometry('230x61')
    app.progress_bar.place(x=0, y=0)
    app.progress_lbl = ttk.Label(app.root, text=f'Generating {entry_name + ".pbt..."}', font=('Helvetica', 8))
    app.progress_lbl.place(x=0, y=23)
    app.progress_uuid = ttk.Label(app.root, text=f'UUID: {uuid}', font=('Helvetica', 8))
    app.progress_uuid.place(x=0, y=40)
    app.root.update()

    app.progress_bar['maximum'] = len(face_maps_by_line)

    mesh_index, current_group = 0, 0
    for triangle_map in face_maps_by_line:  # iterate through each face map
        a, b, c = [], [], []  # reset vectors to empty lists
        maps_gs = [s for s in findall(r'-?\d+\.?\d*/?\d*/?\d*', triangle_map)]
        group = 0 if int(maps_gs[len(maps_gs) - 1]) == 0 else int(maps_gs[len(maps_gs) - 1]) - 1 #Get group index
        if not current_group == group:
            mesh_index = 0
            current_group = group
        texture_name = None
        texture_image = None
        diffuse_color = [1,1,1] #Diffuse color, is multiplied by texture color for color. Solid color for entire material
        texture_color = [1,1,1] #Texture color, the color that is gotten from the texture image with the texture cords specified in the obj
        color = [0,0,0] #Final color
        texture_cords = []
        if group in textures_by_index and app.texturize.get() == 1:
            texture_name = textures_by_index[group]
            if 0 in textures[texture_name]:
                texture_image = textures[texture_name][0]
            if 1 in textures[texture_name]:
                diffuse_color = textures[texture_name][1]


        for vI, vertex in enumerate(triangle_map.split()[:-1]): # Loop through all the triangles in the face
            target_line = vertices_by_line[int(vertex.split('/')[0]) - 1] # Get the line that the v is on. The .split(/) is to get rid of unneeded info
            vertex_position = [float(n) for n in target_line.split(' ')] # Get the position in form [x,y,z]
            if vI == 0: a = vertex_position
            elif vI == 1: b = vertex_position
            elif vI == 2: c = vertex_position
            if len(vertex.split('/')) > 1 and texture_image and app.texturize.get() == 1:
                texture_cord = vertex.split('/')[1]
                if texture_cord != '':
                    cords = texture_cords_by_line[int(texture_cord) - 1].split()
                    cords[0] = max(1, floor(float(cords[0]) * texture_image.width) - 1)
                    cords[1] = max(1, floor(float(cords[1]) * texture_image.height) - 1)
                    texture_cords.append(cords)

        if len(texture_cords) > 0 and app.texturize.get() == 1:
            center = {}
            x1,x2,x3 = texture_cords[0][0], texture_cords[1][0], texture_cords[2][0]
            y1,y2,y3 = texture_cords[0][1], texture_cords[2][1], texture_cords[2][1]
            center[0] = round((x1 + x2 + x3) / 3, 2)
            center[1] = round((y1 + y2 + y3) / 3, 2)
            texture_color = [0,0,0]
            texture_color = np.add(texture_color, np.multiply(np.divide(texture_image.getpixel((center[0], center[1])), 255), 3)[:3]) #Get the color in center of the triangle, count it as half of the color.
            for cord in texture_cords:
                cord_color = np.divide(texture_image.getpixel((cord[0], cord[1]))[:3], 255)
                texture_color = np.add(texture_color, cord_color)
            texture_color = np.divide(texture_color, len(texture_cords) + 3) #Divide to get final texture color for this triangle between 0 and 1

        color = np.multiply(texture_color, diffuse_color) #Multiply the diffuse and texture colors



        core_a = [a[2], -a[0], a[1]] #Convert to Core positions
        core_b = [b[2], -b[0], b[1]]
        core_c = [c[2], -c[0], c[1]]

        position_one, position_two, scale_one, scale_two, rotation_one, rotation_two = triangle(core_a, core_b, core_c, app.optimize.get() == 1)
        app.progress_bar['value'] += 1
        app.root.update_idletasks()
        for position, scale, rotation in zip([position_one, position_two],
                                             [scale_one, scale_two],
                                             [rotation_one, rotation_two]):
            if position is not None and scale is not None and rotation is not None:
                mesh_index += 1
                child_name = "{0}.{1:04}".format(group_names[group] if g_count > 0 else 'mesh', mesh_index)
                folders[group].add_child(child_name, "sm_wedge_002", np.multiply(position, 10), rotation, np.multiply(scale, 10), None, color)
            else:
                continue

    app.set_wrapping_up()
    output_file.write(pbt_output.generate_pbt())
    remove(f'{parent}/{uuid}-vertex.txt'), remove(f'{parent}/{uuid}-map.txt'), remove(f'{parent}/{uuid}-texture.txt')
    input_file.close(), output_file.close()
    app.lbl.place_forget()
    app.aesthetic_path.set('')
    file_path = ''
    app.buttonize()


app.root.mainloop()
