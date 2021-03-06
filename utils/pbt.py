from random import randrange

anti_conflict = []


def generate_id():
    global anti_conflict
    rando = randrange(10 ** 18, 10 ** 19)
    if not rando in anti_conflict:
        anti_conflict.append(rando)
        return f'{rando}'
    else:
        generate_id()


# pbt generator courtesy of Aphrim#1337
class Object:
    def __init__(self, name, position, rotation, scale, parent_id, mesh_id, color, texturize):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.parent_id = parent_id
        self.mesh_id = mesh_id
        self.id = generate_id()
        self.color = color
        self.texturize = texturize

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
                    {f'''UnregisteredParameters {{
                        Overrides {{
                            Name: "ma:Shared_BaseMaterial:color"
                            Color {{
                                R: {min(1, self.color[0])}
                                G: {min(1, self.color[1])}
                                B: {min(1, self.color[2])}
                            }}
                        }}
                        Overrides {{
                            Name: "ma:Shared_BaseMaterial:id"
                            AssetReference {{
                                Id: 6942069420
                            }}
                        }}
                    }}''' if self.texturize else ''}
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
    def __init__(self, root, name, modelize):
        self.id = generate_id()
        self.children = []
        self.root = root
        self.name = name
        self.modelize = modelize

    def add_child(self, name, mesh_name, position, rotation, scale, parent_id, color, texturize):
        mesh_to_add = Object(name, position, rotation, scale, parent_id, self.root.get_mesh_id_for_name(mesh_name), color, texturize)

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
                        {'''Model {
                        }''' if self.modelize else 'IsFilePartition: true'}
                    }}
                }}\n      """
        children_strings = ""
        for object in self.children:
            children_strings += object.generate_pbt_part()

        return this_string + children_strings


class PBT:
    def __init__(self, name, player, camera, texturize, modelize):
        self.template_name = name
        self.player_collision = player
        self.camera_collision = camera
        self.texturize = texturize
        self.modelize = modelize
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
        new_folder = Folder(self, name, self.modelize)
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
          Value: "mc:ecollisionsetting:{self.player_collision}"
        }}
        Visible_v2 {{
          Value: "mc:evisibilitysetting:inheritfromparent"
        }}
        CameraCollidable {{
          Value: "mc:ecollisionsetting:{self.camera_collision}"
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
    Assets {{
      Id: {6942069420 if self.texturize else 5413997507012451432}
      Name: "{"Basic Material" if self.texturize else "sm_wedge_001"}"
      PlatformAssetType: {2 if self.texturize else 1}
      PrimaryAsset {{
        AssetType: "{"MaterialAssetRef" if self.texturize else "StaticMeshAssetRef"}"
        AssetId: "{"mi_basic_pbr_material_001" if self.texturize else "sm_wedge_001"}"
      }}
    }}
    PrimaryAssetId {{
      AssetType: "None"
      AssetId: "None"
    }}
  }}
  SerializationVersion: 92
}}"""
        return pbt
