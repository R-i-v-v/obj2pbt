from __future__ import division
from re import findall, sub
from os import remove
from os.path import splitext, isabs
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, Button, ttk
from random import randrange
import numpy as np
from scipy.spatial.transform import Rotation as R
from PIL import Image
from math import floor, sqrt

# program headed by Rivvnik#1111
np.set_printoptions(16)
anti_conflict, root = [], tk.Tk()
root.title('.obj to .pbt')
root.geometry('60x83')

progress_bar = ttk.Progressbar(root, orient='horizontal', length=120, mode='determinate', value=0)


# pbt generator courtesy of Aphrim#1337
class Object:
    def __init__(self, name, position, rotation, scale, parent_id, mesh_id, color):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.parent_id = parent_id
        self.mesh_id = mesh_id
        self.id = generate_id()
        self.color = color

    def generate_pbt_part(self):
        return f"""Objects {{
                    Id: {self.id}
                    Name: "{self.name}"
                    Transform {{
                    Location {{
                        X: {self.position[0]}
                        Y: {self.position[1]}
                        Z: {self.position[2]}
                    }}
                    Rotation {{
                        Pitch: {self.rotation[1]}
                        Yaw: {self.rotation[2]}
                        Roll: {self.rotation[0]}
                    }}
                    Scale {{
                        X: {self.scale[0]}
                        Y: {self.scale[1]}
                        Z: {self.scale[2]}
                    }}
                    }}
                    ParentId: {self.parent_id}    
                    UnregisteredParameters {{
                        Overrides {{
                            Name: "ma:Shared_BaseMaterial:color"
                            Color {{
                                R: {min(1, self.color[0])}
                                G: {min(1, self.color[1])}
                                B: {min(1, self.color[2])}
                            }}
                        }}
                    }}
                    Collidable_v2 {{
                    Value: "mc:ecollisionsetting:inheritfromparent"
                    }}
                    Visible_v2 {{
                    Value: "mc:evisibilitysetting:inheritfromparent"
                    }}
                    CameraCollidable {{
                    Value: "mc:ecollisionsetting:inheritfromparent"
                    }}
                    EditorIndicatorVisibility {{
                    Value: "mc:eindicatorvisibility:visiblewhenselected"
                    }}
                    CoreMesh {{
                    MeshAsset {{
                        Id: {self.mesh_id}
                    }}
                    Teams {{
                        IsTeamCollisionEnabled: true
                        IsEnemyCollisionEnabled: true
                    }}
                    StaticMesh {{
                        Physics {{
                        Mass: 100
                        LinearDamping: 0.01
                        }}
                        BoundsScale: 1
                    }}
                    }}
                }}\n      """


class Folder:
    def __init__(self, root, name):
        self.id = generate_id()
        self.children = []
        self.root = root
        self.name = name

    def add_child(self, name, mesh_name, position, rotation, scale, parent_id, color):
        mesh_to_add = Object(name, position, rotation, scale, parent_id, self.root.get_mesh_id_for_name(mesh_name), color)

        if mesh_to_add.parent_id is None:
            mesh_to_add.parent_id = self.id

        if mesh_to_add.position is None:
            mesh_to_add.position = [0, 0, 0]

        if mesh_to_add.rotation is None:
            mesh_to_add.rotation = [0, 0, 0]

        if mesh_to_add.scale is None:
            mesh_to_add.scale = [1, 1, 1]

        self.children.append(mesh_to_add)
        return mesh_to_add

    def children_to_string(self):
        children_string = ""
        for object in self.children:
            children_string += f"ChildIds: {object.id}\n        "
        return children_string

    def generate_pbt_part(self):
        this_string = f"""
                Objects {{
                    Id: {self.id}
                    Name: "{self.name}"
                    Transform {{
                        Location {{
                        }}
                        Rotation {{
                        }}
                        Scale {{
                            X: {1}
                            Y: {1}
                            Z: {1}
                        }}
                    }}
                    ParentId: {self.root.root_id}    
                    {self.children_to_string()}
                    Collidable_v2 {{
                    Value: "mc:ecollisionsetting:inheritfromparent"
                    }}
                    Visible_v2 {{
                    Value: "mc:evisibilitysetting:inheritfromparent"
                    }}
                    CameraCollidable {{
                    Value: "mc:ecollisionsetting:inheritfromparent"
                    }}
                    EditorIndicatorVisibility {{
                    Value: "mc:eindicatorvisibility:visiblewhenselected"
                    }}
                    Folder {{
                        IsFilePartition: true
                    }}
                }}\n      """
        children_strings = ""
        for object in self.children:
            children_strings += object.generate_pbt_part()

        return this_string + children_strings


class PBT:
    def __init__(self, name):
        self.template_name = name
        self.template_id = generate_id()
        self.root_id = generate_id()
        self.objects = []
        self.meshes_by_id = []

    def get_mesh_id_for_name(self, mesh_name):
        for mesh in self.meshes_by_id:
            if mesh['name'] == mesh_name:
                return mesh['id']
        new_mesh = {"id": generate_id(), "name": mesh_name}
        self.meshes_by_id.append(new_mesh)
        return new_mesh['id']

    def add_folder(self, name):
        new_folder = Folder(self, name)
        self.objects.append(new_folder)
        return new_folder

    def children_to_string(self):
        children_string = ""
        for object in self.objects:
            children_string += f"ChildIds: {object.id}\n        "
        return children_string

    def all_objects_pbt(self):
        all_objects_string = ""

        for object in self.objects:
            object_string = object.generate_pbt_part()
            all_objects_string += object_string
        return all_objects_string

    def object_assets_pbt(self):
        assets_string = ""
        for mesh in self.meshes_by_id:
            mesh_asset_string = f"""Assets {{
      Id: {mesh['id']}
      Name: "{mesh['name']}"
      PlatformAssetType: 1
      PrimaryAsset {{
        AssetType: "StaticMeshAssetRef"
        AssetId: "{mesh['name']}"
      }}
    }}"""
            assets_string += mesh_asset_string
        return assets_string

    def generate_pbt(self):
        pbt = f"""Assets {{
  Id: {self.template_id}
  Name: "{self.template_name}"
  PlatformAssetType: 5
  TemplateAsset {{
    ObjectBlock {{
      RootId: {self.root_id}
      Objects {{
        Id: {self.root_id}
        Name: "Folder"
        Transform {{
          Scale {{
            X: 1
            Y: 1
            Z: 1
          }}
        }}
        ParentId: {generate_id()}
        {self.children_to_string()}Collidable_v2 {{
          Value: "mc:ecollisionsetting:inheritfromparent"
        }}
        Visible_v2 {{
          Value: "mc:evisibilitysetting:inheritfromparent"
        }}
        CameraCollidable {{
          Value: "mc:ecollisionsetting:inheritfromparent"
        }}
        EditorIndicatorVisibility {{
          Value: "mc:eindicatorvisibility:visiblewhenselected"
        }}
        Folder {{
          IsGroup: true
        }}
      }}
      {self.all_objects_pbt()[:-2]}}}
    {self.object_assets_pbt()}
    PrimaryAssetId {{
      AssetType: "None"
      AssetId: "None"
    }}
  }}
  SerializationVersion: 92
}}"""
        return pbt


def open_file():
    root.withdraw()
    file_path = filedialog.askopenfilename()
    run(file_path)


btn = Button(root, text='select\ntriangulated\n.obj file', width=10, height=3, font=('Helvetica bold', 14), fg='black', command=open_file)
btn.place(x=0, y=0)


def generate_id():
    global anti_conflict
    rando = randrange(10 ** 18, 10 ** 19)
    if not rando in anti_conflict:
        anti_conflict.append(rando)
        return f'{rando}'
    else:
        generate_id()


# triangle splitting and rotating function courtesy of waffle#3956
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

    thickness = 0.02
    r = np.multiply(x if flip else -x, thickness)

    position_1 = np.add([(c[0] + a[0] + r[0]) * .5, (c[1] + a[1] + r[1]) * .5, (c[2] + a[2] + r[2]) * .5], np.multiply(z, width_1 / 2))
    position_2 = np.subtract([(c[0] + b[0] + r[0]) * .5, (c[1] + b[1] + r[1]) * .5, (c[2] + b[2] + r[2]) * .5], np.multiply(z, width_2 / 2))
    scale_1, scale_2 = np.divide([thickness, len_1, width_1], 100), np.divide([thickness, len_1, width_2], 100)
    matrix_1, matrix_2 = np.transpose([x, -y, -z]), np.transpose([-x, -y, z])
    rotation_1 = R.from_matrix(matrix_1).as_euler('xyz', degrees=True) * [-1, -1, 1]
    rotation_2 = R.from_matrix(matrix_2).as_euler('xyz', degrees=True) * [-1, -1, 1]
    return position_1, position_2, scale_1, scale_2, rotation_1, rotation_2


def run(path):
    if path == '':
        root.destroy()
        return
    entry_name = str(Path(splitext(path)[0])).split('\\')[-1:][0]
    parent = str(Path(path).parent)
    pbt_output = PBT(name=f'{entry_name}')

    # reset vertex, map, and output if they exist
    # read input and output files into memory
    open(f'{parent}/vertex.txt', 'w').close(), open(f'{parent}/map.txt', 'w').close()
    open(f'{parent}/{entry_name}.pbt', 'w').close()
    vertex_file, map_file, texture_cords_file = open(f'{parent}/vertex.txt', 'a'), open(f'{parent}/map.txt', 'a'), open(f'{parent}/texturecords.txt', 'a')
    input_file, output_file, mtl_file = open(f'{path}', 'r'), open(f'{parent}/{entry_name}.pbt', 'a'), None
    input_lines = input_file.readlines()
    textures_by_index, textures = {}, {} #textures_by_index corresponds to the mat name of a group, textures is the actual texture data of a texture with the mat name being used as key.

    # extract vertices, face-maps, and groups from input .obj file
    object_number, g_count = 1, 0
    folders = []
    for line in input_lines:
        if line.startswith('v '):
            vertex_file.write(line[2:])
        elif line.startswith('g ') or line.startswith('o '):
            object_number += 1
            g_count += 1
            folders.append(pbt_output.add_folder(f"Group {g_count - 1}"))
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
    vertices_by_line = [n.strip() for n in open(f'{parent}/vertex.txt', 'r').readlines()]
    face_maps_by_line = [n.strip() for n in open(f'{parent}/map.txt', 'r').readlines()]
    texture_cords_by_line = [n.strip() for n in open(f'{parent}/texturecords.txt', 'r').readlines()]


    if mtl_file != None:
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

                
                    

    btn.place_forget()
    root.deiconify()
    progress_bar.place(x=0, y=0)
    root.geometry('60x21')
    root.update()

    progress_bar['maximum'] = len(face_maps_by_line)

    if len(face_maps_by_line[0].split()) > 4: #If model isn't triangulated shows a warning
        warning_lbl = ttk.Label(root, text='Please Triangulate Model', font=('Helvetica bold', 7))
        warning_lbl.place(x=0, y=21)
        root.geometry('60x41')
        root.update()


    for triangle_map in face_maps_by_line:  # iterate through each face map
        a, b, c = [], [], []  # reset vectors to empty lists
        maps_gs = [s for s in findall(r'-?\d+\.?\d*/?\d*/?\d*', triangle_map)]
        group = 0 if int(maps_gs[len(maps_gs) - 1]) == 0 else int(maps_gs[len(maps_gs) - 1]) - 1 #Get group index

        texture_name = None
        texture_image = None
        diffuse_color = [1,1,1] #Diffuse color, is multiplied by texture color for color. Solid color for entire material
        texture_color = [1,1,1] #Texture color, the color that is gotten from the texture image with the texture cords specified in the obj
        color = [0,0,0] #Final color
        texture_cords = []
        if group in textures_by_index:
            if texture_name in textures_by_index:
                texture_name = textures_by_index[group]
                if 0 in textures[texture_name]:
                    texture_image = textures[texture_name][0]
                if 1 in textures[texture_name]:
                    diffuse_color = textures[texture_name][1]


        for vI, vertex in enumerate(triangle_map.split()[:-1]): # Loop through all the triangles in the face
            target_line = vertices_by_line[int(vertex.split('/')[0]) - 1] # Get the line that the v is on. The .split(/) is to get rid of unneeded info
            vertex_position = [float(n) for n in target_line.split(' ')] # Get the position in form [x,y,z]
            if vI == 0: a = vertex_position;
            elif vI == 1: b = vertex_position;
            elif vI == 2: c = vertex_position;
            if len(vertex.split('/')) > 1 and texture_image:
                texture_cord = vertex.split('/')[1]
                if texture_cord != '':
                    cords = texture_cords_by_line[int(texture_cord) - 1].split()
                    cords[0] = max(1, floor(float(cords[0]) * texture_image.width) - 1)
                    cords[1] = max(1, floor(float(cords[1]) * texture_image.height) - 1)
                    texture_cords.append(cords)

        if len(texture_cords) > 0:
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
        position_one, position_two, scale_one, scale_two, rotation_one, rotation_two = triangle(core_a, core_b, core_c)
        progress_bar['value'] += 1
        root.update_idletasks()
        for position, scale, rotation in zip([position_one, position_two],
                                             [scale_one, scale_two],
                                             [rotation_one, rotation_two]):
            # the following if statement only useful when we get right triangle checker implemented
            if position is not None and scale is not None and rotation is not None:
                folders[group].add_child('testMesh', "sm_wedge_001", np.multiply(position, 10), rotation, np.multiply(scale, 10), None, color)
            else:
                continue

    progress_bar.place_forget()
    root.update()
    lbl = ttk.Label(root, text='wrapping up...', font=('Helvetica bold', 8))
    lbl.place(x=0, y=0)
    root.update()
    output_file.write(pbt_output.generate_pbt())
    remove(f'{parent}/vertex.txt'), remove(f'{parent}/map.txt'), remove(f'{parent}/texturecords.txt')
    input_file.close(), output_file.close()
    root.destroy()


root.mainloop()