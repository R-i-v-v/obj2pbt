import random

def generateId():
    return str((random.random() * pow(10,12)))[0:10]

class Object:
    def __init__(self, tableParams):
        self.name = tableParams["name"]
        self.position = tableParams["position"]
        self.rotation = tableParams["rotation"]
        self.scale = tableParams["scale"]
        self.parentId = tableParams["parentId"]
        self.meshId = tableParams["meshId"]
        self.id = generateId()

class pbtGenerator:
    def __init__(self, tableParams):
        self.templateName = tableParams["templateName"]
        self.templateId = generateId()
        self.rootId = generateId()
        self.objects = []
        self.meshIds = []
    
    def getMeshIdForName(self, meshName):
        for mesh in self.meshIds:
            if (mesh.name == meshName):
                return mesh.id
        newMeshId = {"id": generateId(), "name": meshName}
        self.meshIds.append(newMeshId)
        return newMeshId
    
    def addMesh(self, name, meshName, tableParams):
        meshToAdd = Object(
        {
            "name": name,
            "position": tableParams["position"],
            "rotation": tableParams["rotation"],
            "scale": tableParams["scale"],
            "parentId": tableParams["parentId"],
            "meshId": self.getMeshIdForName(meshName),
            "id": generateId()
        })

        if (meshToAdd.parentId is None):
            meshToAdd.parentId = self.rootId

        if (meshToAdd.position is None):
            meshToAdd.position = [0,0,0]

        if (meshToAdd.rotation is None):
            meshToAdd.rotation = [0,0,0]

        if (meshToAdd.scale is None):
            meshToAdd.scale = [1,1,1]
        
        self.objects.append(meshToAdd)
        return meshToAdd
    
    def childrenToString(self):
        childrenString = ""
        for object in self.objects:
            childrenString += "\n ChildIds: " + object.id
        return childrenString

    def allObjectsPBT(self):
        allObjectsString = ""

        for object in self.objects:
            objectString = f'''
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
                                ParentId: {self.rootId}    
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
                                        Id: {object.meshId['id']}
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
                            '''
            allObjectsString += objectString
        return allObjectsString

    def objectAssetsPBT(self):     
        assetsString = ""
        for meshId in self.meshIds:
            meshAssetString = f'''
                Assets {{
                    Id: {meshId['id']}
                    Name: "{meshId['name']}"
                    PlatformAssetType: 1
                    PrimaryAsset {{
                        AssetType: "StaticMeshAssetRef"
                        AssetId: "{meshId['name']}"
                    }}
                }}
            '''
            assetsString += meshAssetString
        return assetsString

    def generatePBT(self):
        pbt = f'''
            Assets {{
                Id: {self.templateId}
                Name: "{self.templateName}"
                PlatformAssetType: 5
                TemplateAsset {{
                    ObjectBlock {{
                        RootId: {self.rootId}
                        Objects {{
                            Id: {self.rootId}
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
                            {self.childrenToString()}
                            Folder {{
                                IsGroup: true
                            }}
                        }}
                        {self.allObjectsPBT()}
                    }}
                    {self.objectAssetsPBT()}
                    PrimaryAssetId {{
                        AssetType: "None"
                        AssetId: "None"
                    }}
                }}
                SerializationVersion: 92
            }}
        '''
        return pbt




myPBT = pbtGenerator({"templateName": 'EpicPythonGeneratedTemplate'})
myPBT.addMesh('testMesh', 'sm_cube_002', {"position": [100,200,300], "rotation": None, "scale": None, "parentId": None})
print(myPBT.generatePBT())