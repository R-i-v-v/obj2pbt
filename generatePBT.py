import random

def generate_id():
    return f'{random.randrange(10**19, 10**20)}'

class Object:
    def __init__(self, name, position, rotation, scale, parent_id, mesh_id):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.parent_id = parent_id
        self.mesh_id = mesh_id
        self.id = generate_id()

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
        return new_mesh
    
    def add_mesh(self, name, mesh_name, position, rotation, scale, parent_id):
        mesh_to_add = Object(name, position, rotation, scale, parent_id, self.get_mesh_id_for_name(mesh_name))

        if mesh_to_add.parent_id is None:
            mesh_to_add.parent_id = self.root_id

        if mesh_to_add.position is None:
            mesh_to_add.position = [0, 0, 0]

        if mesh_to_add.rotation is None:
            mesh_to_add.rotation = [0, 0, 0]

        if mesh_to_add.scale is None:
            mesh_to_add.scale = [1, 1, 1]
        
        self.objects.append(mesh_to_add)
        return mesh_to_add
    
    def children_to_string(self):
        children_string = ""
        for object in self.objects:
            children_string += "\n ChildIds: " + object.id
        return children_string

    def all_objects_pbt(self):
        all_objects_string = ""

        for object in self.objects:
            object_string = f"""
                            Objects {{
                                Id: {object.id}
                                Name: "{object.name}"
                                Transform {{
                                    Location {{
                                        X: {object.position[0]}
                                        Y: {object.position[1]}
                                        Z: {object.position[2]}
                                    }}
                                    Rotation {{
                                        Pitch: {object.rotation[0]}
                                        Yaw: {object.rotation[1]}
                                        Roll: {object.rotation[2]}
                                    }}
                                    Scale {{
                                        X: {object.scale[0]}
                                        Y: {object.scale[1]}
                                        Z: {object.scale[2]}
                                    }}
                                }}
                                ParentId: {self.root_id}    
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
                                        Id: {object.mesh_id}
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
                            }} \n
                            """
            all_objects_string += object_string
        return all_objects_string

    def object_assets_pbt(self):     
        assets_string = ""
        for mesh in self.meshes_by_id:
            mesh_asset_string = f"""
                Assets {{
                    Id: {mesh['id']}
                    Name: "{mesh['name']}"
                    PlatformAssetType: 1
                    PrimaryAsset {{
                        AssetType: "StaticMeshAssetRef"
                        AssetId: "{mesh['name']}"
                    }}
                }}
            """
            assets_string += mesh_asset_string
        return assets_string

    def generate_pbt(self):
        pbt = f"""
            Assets {{
                Id: {self.template_id}
                Name: "{self.template_name}"
                PlatformAssetType: 5
                TemplateAsset {{
                    ObjectBlock {{
                        RootId: {self.root_id}
                        Objects {{
                            Id: {self.root_id}
                            Name: "Group"
                            Transform {{
                                Location {{
                                }}
                                Rotation {{
                                }}
                                Scale {{
                                    X: 1
                                    Y: 1
                                    Z: 1
                                }}
                            }}
                            {self.children_to_string()}
                            Folder {{
                                IsGroup: true
                            }}
                        }}
                        {self.all_objects_pbt()}
                    }}
                    {self.object_assets_pbt()}
                    PrimaryAssetId {{
                        AssetType: "None"
                        AssetId: "None"
                    }}
                }}
                SerializationVersion: 92
            }}
        """
        return pbt



b'''
myPBT = PBT({"template_name": 'EpicPythonGeneratedTemplate'})
myPBT.add_mesh('testMesh', 'sm_cube_002', {"position": [100,200,300], "rotation": None, "scale": None, "parent_id": None})
print(myPBT.generate_pbt())
'''