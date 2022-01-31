from __future__ import division
from re import findall
from os import remove, scandir
from os.path import splitext, exists
from pathlib import Path, PurePath
from tkinter import filedialog, ttk
import ctypes
import numpy as np
from uuid import uuid4
from math import floor
from time import time
from decimal import Decimal

from utils.pbt import PBT
from utils.icon import icon_in_base_64
from utils.calc import triangle
from utils.gui import UI
from utils.file import readData

# program headed by Rivvnik#1111
np.set_printoptions(16)
myappid = u'mycompany.myproduct.subproduct.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = None  # set taskbar icon


def open_file():
    global file_path, pure_path, dir_path
    if app.log.get() == 1:
        dir_path = filedialog.askdirectory()
        try:
            dir_name = PurePath(dir_path).parts[-1]
            file_path = None
            app.aesthetic_path.set(f'../{dir_name}/')
        except Exception as e:
            print(f"Caught '{e}'")
    else:
        file_path = filedialog.askopenfilename(filetypes=[('Wavefront objects', '*.obj'), ('All files', '*.*')])
        path_name = PurePath(file_path).name
        if len(path_name[:-4]) > 16:
            path_name = path_name[:12] + '...' + path_name[-7:]
        app.aesthetic_path.set(f"{path_name}")


def convert_file():
    global file_path, dir_path
    if not file_path == '':
        app.root.withdraw()
        if app.log.get() == 1:
            run(dir_path)
        else:
            run(file_path)
    else:
        open_file()


app = UI()
app.version(3.1)
app.ui_init(icon_in_base_64, convert_file, open_file)
app.buttonize()


def run(path):
    global file_path
    parent = str(Path(path).parent) if not Path(path).is_dir() else str(path)
    if app.log.get() == 1 and not exists(Path(f'{parent}/log.csv')):
        open(f'{parent}/log.csv', 'w').write('File name\tFace count\tTime elapsed (ms)\n')
    entries = []
    if not file_path:
        with scandir(path) as dirs:
            for entry in dirs:
                entries.append(entry)
    if not entries:
        entries = range(1)
    for some_file in entries:
        if entries != range(1):
            if some_file.name.endswith('obj'):
                path = some_file.path
            else:
                continue
        start_time = time()
        entry_name = str(Path(splitext(path)[0])).split('\\')[-1:][0]
        player, camera = app.setting()
        pbt_output = PBT(name=f'{entry_name}', player=player, camera=camera,
                         texturize=app.texturize.get() == 1,
                         modelize=app.modelize.get() == 1)

        # give vertex, and map files uuids, create output pbt
        # read input and output files into memory
        uuid = str(uuid4()).split('-')[-1:][0]
        open(f'{parent}/{uuid}-vertex.txt', 'w').close()
        open(f'{parent}/{uuid}-map.txt', 'w').close()
        open(f'{parent}/{entry_name}.pbt', 'w').close()

        app.unplace()
        app.root.deiconify()
        app.root.geometry('230x61')
        app.progress_bar.place(x=0, y=0)
        app.progress_lbl = ttk.Label(app.root, text=f'Generating {entry_name + ".pbt..."}', font=('Helvetica', 8))
        app.progress_lbl.place(x=0, y=23)
        app.progress_uuid = ttk.Label(app.root, text=f'UUID: {uuid}', font=('Helvetica', 8))
        app.progress_uuid.place(x=0, y=40)
        app.root.update()

        (
            vertices_by_line,
            face_maps_by_line,
            texture_cords_by_line,
            textures_by_index,
            textures, folders,
            group_names,
            output_file,
            input_file,
            log_file,
            g_count,
            face_count
        ) = readData(path, uuid, parent, pbt_output, entry_name, app.texturize.get() == 1, app.log.get() == 1)
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

            # Multiply the diffuse and texture colors
            color = np.multiply(texture_color, diffuse_color)  # if app.texturize.get() == 1 else [0.118, 0.141, 0.384]

            core_a = [a[2], a[0], a[1]] #Convert to Core positions
            core_b = [b[2], b[0], b[1]]
            core_c = [c[2], c[0], c[1]]

            shapes = triangle(core_a, core_b, core_c, app.optimize.get() == 1)
            app.progress_bar['value'] += 1
            app.root.update_idletasks()
            for shape in shapes:
                    mesh_index += 1
                    child_name = "{0}.{1:04}".format(group_names[group] if g_count > 0 else 'mesh', mesh_index)
                    folders[group].add_child(child_name, shape.type, np.multiply(shape.position, 10), shape.rotation, np.multiply(shape.scale, 10), None, color, app.texturize.get() == 1)

        app.set_wrapping_up(uuid, entry_name)
        output_file.write(pbt_output.generate_pbt())
        remove(f'{parent}/{uuid}-vertex.txt'), remove(f'{parent}/{uuid}-map.txt'), remove(f'{parent}/{uuid}-texture.txt')
        input_file.close(), output_file.close()
        app.lbl.place_forget()
        app.separator.place_forget()
        app.name_lbl.place_forget()
        app.uuid_lbl.place_forget()
        app.aesthetic_path.set('')
        file_path = ''
        if log_file:
            log_file.write(f'{entry_name}\t{face_count}\t{round(Decimal(time()-start_time)*1000,3)}\n')
    app.buttonize()


app.root.mainloop()
