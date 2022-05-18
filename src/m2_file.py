

#from . import BSP_Tree
#from .BSP_Tree import *

#from . import Collision
#from .Collision import *

import bpy
import math
from math import *
import bmesh
from mathutils import Vector, Quaternion, Matrix
import os
import m2_format
from m2_format import M2Header, M2SkinProfile, C3Vector
from configparser import ConfigParser
import bpy
import dbcpy
from dbcpy.dbc_file import DBCFile
from fileinput import filename
import mathutils
#from test.badsyntax_future3 import result

    
def add_obj(data, obj_name, collection=None):
    
    if collection is None:
        collection = bpy.context.collection

    new_obj = bpy.data.objects.new(obj_name, data)
    collection.objects.link(new_obj)
    new_obj.select_set(state=True)

    if bpy.context.view_layer.objects.active is None or bpy.context.view_layer.objects.active.mode == 'OBJECT':
        bpy.context.view_layer.objects.active = new_obj
    return new_obj

def add_empty(empty_name, collection=None):
    if collection is None:
        collection = bpy.context.collection
    empty_obj = bpy.data.objects.new(empty_name, None)
    collection.objects.link(empty_obj)
    return empty_obj

def array_to_str(m2_array):
    result = ''
    for i in range(len(m2_array) - 1):
        result += m2_array[i].decode("utf-8")
    return result

def find_model_by_name(modelname, config):
    result = None
    def is_equal(obj, other):
        obj = obj.replace('\\', '/')
        obj = obj.split('/')
        obj = obj[len(obj)-1]
        obj = obj.split('.')
        obj = obj[0]
        obj = obj.strip().lower()

        other = other.replace('\\', '/')
        other = other.split('/')
        other = other[len(other)-1]
        other = other.split('.')
        other = other[0]
        other = other.strip().lower()
        return (obj == other)
    
    pathname = config['DBC_FILES']['PATH']
    name = "CreatureModelData"
    
    with open(f"{pathname}\\{name}.dbc", 'r+b') as f:
        dbc_file = DBCFile.from_file(f, eval(f"dbcpy.records.{name}Rec"))
        for rec in dbc_file.records:
            if is_equal(modelname, rec.ModelPath.value):
                result = rec
                break
            
    return result

def find_creature_display_info(modelid, config):
    result = None
    
    pathname = config['DBC_FILES']['PATH']
    name = "CreatureDisplayInfo"
    
    with open(f"{pathname}\\{name}.dbc", 'r+b') as f:
        dbc_file = DBCFile.from_file(f, eval(f"dbcpy.records.{name}Rec"))
        for rec in dbc_file.records:
            if rec.ModelID == modelid:
                result = rec
                break
            
    return result


def find_animation_data(id, config):
    result = None
    
    pathname = config['DBC_FILES']['PATH']
    name = "AnimationData"
    
    with open(f"{pathname}\\{name}.dbc", 'r+b') as f:
        dbc_file = DBCFile.from_file(f, eval(f"dbcpy.records.{name}Rec"))
        for rec in dbc_file.records:
            if rec.ID == id:
                result = rec
                break
            
    return result

class Blender:
    RIGHT = Vector((1,0,0))
    LEFT = RIGHT * -1
    FORWARD = Vector((0,1,0))
    BACKWARD = FORWARD * -1
    UP = Vector((0,0,1))

class M2File:
    config: ConfigParser
    header: M2Header
    context: bpy.context
    scene: bpy.context.scene
    modelName : str
    modelId: int
    path: str
    base: str
    arm: bpy.types.Armature
    rig: bpy.types.Object
    materials: []
    meshes: []
    skins: []
    
    
    def __init__(self, config):
         
        self.header = M2Header()
        self.context = None
        self.scene = None
        self.modelName = ""
        self.modelId = 0
        self.arm = None
        self.rig = None
        self.path = ""
        self.skins = []
        self.meshes = []
        self.materials = []
        self.config = config
        self.base = ""
        
        
    def read(self, f):        
        # Basisverzeichnis 
        self.base = self.config['DBC_FILES']['PATH']

        self.archive = self.config['MODELS']['PATH']
        
        
        self.path = os.path.dirname(f.name)
        self.header.read(f) 
    
        # Modellnamen aus dem Header lesen,
        # Hinweis:
        #   Dies ist eine Null-Teminiertere Zeichenfolge
        self.modelName = array_to_str(self.header.name)

        rec = find_model_by_name(self.modelName, self.config)
        if rec != None:
            self.modelId = rec.ID
        

    def createBlender(self) -> None:
        self.context = bpy.context
        self.scene = self.context.scene

        #deselect all objects.
        #bpy.ops.object.select_all(action = 'DESELECT')

        # instantiate armature
        #bpy.ops.object.add(type = 'ARMATURE', enter_editmode = True, location = (0.0, 0.0, 0.0))
        #self.arm = bpy.context.object
        
        self.arm = bpy.data.armatures.new(self.modelName + ".Skelett")
        self.rig = bpy.data.objects.new(self.modelName + ".Skelett", self.arm)
        self.rig.location = (0, 0, 0)
        #rig.show_x_ray = self.enable_armature_xray
        #armature.show_names = self.display_bone_names

        # Link the object to the scene
        self.scene.collection.objects.link(self.rig)
        self.context.view_layer.objects.active = self.rig
        
        self.createBones()
        self.createSkins()
        self.createTextures()
        self.createAnimations()
        print("Ferdsch")
        
    def createAnimations(self):
        bone_adjust = []
        #f = open("c:/Anhang/anim.txt", "w")
        bpy.ops.object.mode_set(mode='POSE')
        for pbone in self.rig.pose.bones.values():
            row1 = [pbone.location[0], pbone.rotation_quaternion[1], pbone.scale[0]]
            row2 = [pbone.location[1], pbone.rotation_quaternion[2], pbone.scale[1]]
            row3 = [pbone.location[2], pbone.rotation_quaternion[3], pbone.scale[2]]
            row4 = [0, pbone.rotation_quaternion[0], 0]
            bone_adjust.append(Matrix([row1, row2, row3, row4]))
            
            
        seq_id = 0

        for seq_id in range(len(self.header.sequences)):
        #for seq_id in range(0, 1):
            seq = self.header.sequences[seq_id]
            rec = find_animation_data(seq.animation_id, self.config)
            anim = self.rig.animation_data_create()
            action = bpy.data.actions.new(f"{self.rig.name}.Action.{seq_id:03d}.{rec.Name.value}")
            anim.action = action
            self.createSequence(seq_id, seq.length, action, None, bone_adjust)
            #seq_id += 1
        bpy.ops.object.mode_set(mode='POSE')
        #f.close()
        
    def createSequence(self, id, lenght, action, file, start):
        def fromRotationMatrix(m):
            """
            // Use the Graphics Gems code, from 
            // ftp://ftp.cis.upenn.edu/pub/graphics/shoemake/quatut.ps.Z
            // *NOT* the "Matrix and Quaternions FAQ", which has errors!
        
            // the trace is the sum of the diagonal elements; see
            // http://mathworld.wolfram.com/MatrixTrace.html
            """
            t = m[0][0] + m[1][1] + m[2][2];

            # we protect the division by s by ensuring that s>=1
            if (t >= 0): # // |w| >= .5
                s = math.sqrt(t+1) # |s|>=1 ...
                w = 0.5 * s
                s = 0.5 / s                 # so this division isn't bad
                x = (m[2][1] - m[1][2]) * s
                y = (m[0][2] - m[2][0]) * s
                z = (m[1][0] - m[0][1]) * s
            elif ((m[0][0] > m[1][1]) and (m[0][0] > m[2][2])):
                s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) # |s|>=1
                x = s * 0.5 # |x| >= .5
                s = 0.5 / s
                y = (m[1][0] + m[0][1]) * s
                z = (m[0][2] + m[2][0]) * s
                w = (m[2][1] - m[1][2]) * s
            elif (m[1][1] > m[2][2]):
                s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) # |s|>=1
                y = s * 0.5 #|y| >= .5
                s = 0.5 / s
                x = (m[1][0] + m[0][1]) * s
                z = (m[2][1] + m[1][2]) * s
                w = (m[0][2] - m[2][0]) * s
            else:
                s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) # |s|>=1
                z = s * 0.5 # |z| >= .5
                s = 0.5 / s
                x = (m[0][2] + m[2][0]) * s
                y = (m[2][1] + m[1][2]) * s
                w = (m[1][0] - m[0][1]) * s
            
            return mathutils.Quaternion((w, x, y, z));            
        
        def MultiplyQuat(q1, q2):
            w = q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z
            x = q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y
            y = q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x
            z = q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w
            return Quaternion([w,x,y,z])
        
        def MakeFloat(v):
            f = 0
            if v > 0:
                f = v - 32767
            else:
                f = v + 32767

            return (f / 32767.0)
        
        def AddKeyFrames(frame):
            for i in range (len(self.rig.pose.bones.keys())):
                name = self.rig.pose.bones.keys()[i]
                pbone = self.rig.pose.bones[name]
                pbone.keyframe_insert(data_path="location", index=-1, frame=frame)
                pbone.keyframe_insert(data_path="rotation_quaternion", index=-1, frame=frame)
                pbone.keyframe_insert(data_path="scale", index=-1, frame=frame)
        
        
        
        print(f"createSequence(id={id}, lenght={lenght}, action={action.name})")
        
        # StartFrame
        #for i in range (len(self.rig.pose.bones.keys())):
            #name = self.rig.pose.bones.keys()[i]
            #pbone = self.rig.pose.bones[name]
            #sbone = start[i]
            #pbone.location = Vector([sbone[0][0], sbone[1][0], sbone[2][0]])
            #pbone.rotation_quaternion = Quaternion([sbone[3][1], sbone[0][1], sbone[1][1], sbone[2][1]])
            #pbone.scale = Vector([sbone[0][2], sbone[1][2], sbone[2][2]])
        
        # AddKeyFrames(0)    
        # Aktion für die aktuelle Sequenz auswählen
        #bpy.data.actions[action.name]
        
        # Alle möglichen Zeitstempel durchlaufen und
        # mit den vorhandenen Zeitstempeln der 
        # Sequenz/Bones vergleichen 
        #for stamp in range(0,10):
        for stamp in range(lenght):
            flag_translation = False
            flag_rotation = False
            flag_scale = False

            for pair in range(len(self.header.bones)):
                bonename = f"Bone_{pair:03d}"
                bone = self.header.bones[pair]
                bone.calculateMatrixJme(id, stamp)
                
                frame = bone.translation.getFrameNumber(id, stamp)
                if(frame != -1 and bone.translation.getTimelineTimes(id)[frame] == stamp):
                    flag_translation = True            
                
                frame = bone.rotation.getFrameNumber(id, stamp) 
                if(frame != -1 and bone.rotation.getTimelineTimes(id)[frame] == stamp):
                    flag_rotation = True
                
                frame = bone.scale.getFrameNumber(id, stamp)
                if(frame != -1 and bone.scale.getTimelineTimes(id)[frame] == stamp):
                    flag_scale = True
             
            if (not flag_rotation and not flag_translation and not flag_scale):
                continue
                                
            # Zeitstempel der Bonespaare abgeleichen 
            for pair in range(len(self.header.bones)):
                bonename = f"Bone_{pair:03d}"
                # M2-Bone
                bone = self.header.bones[pair]
                #bone.calculateMatrixJme(id, stamp)
                
                # Blender-Bone
                bbone = self.rig.pose.bones[bonename]
                
                # Translation des aktuellen Bones ermitteln
                # Frame fuer den aktuellen Zeitstempel
                mat = bone.lastCalcMatrix
                bbone.rotation_mode = "QUATERNION"
                
                if mat != None:
                    vec = mat.to_translation()
                    bbone.location = vec
                
                print(f"Sequence: {action.name} Frame: {stamp:04d} Bone: {bbone.name} Translation: {bbone.location}")
                bbone.keyframe_insert(data_path="location", index=-1, frame=stamp)
                
                # Rotation des aktuellen Bones ermitteln
                # Frame fuer den aktuellen Zeitstempel
                print(f"Sequence: {action.name} Frame: {stamp:04d} Bone: {bbone.name} Rotation: {bbone.rotation_quaternion}")
                if mat != None:
                    quart = fromRotationMatrix(mat)
                    bbone.rotation_mode = "QUATERNION"
                    bbone.rotation_quaternion = quart
                    #bbone.rotation_mode = "ZXY"
                    #bbone.rotation_euler[2] = yaw #yaw
                    #bbone.rotation_euler[0] = roll #roll
                    #bbone.rotation_euler[1] = -pitch  #pitch
                    
                #print(f"{bbone.name} (yaw={math.degrees(yaw)}, roll={math.degrees(roll)} pitch={math.degrees(pitch)})")
                bbone.keyframe_insert(data_path="rotation_quaternion", index=-1, frame=stamp)
                    
                # Frame fuer den aktuellen Zeitstempel
                print(f"Sequence: {action.name} Frame: {stamp:04d} Bone: {bbone.name} Scale: {bbone.scale}")
                vec = bone.lastScaling
                bbone.scale = vec
                bbone.keyframe_insert(data_path="scale", index=-1, frame=stamp)
                    

    
    def createTextures(self) -> None:
        rec = find_creature_display_info(self.modelId, self.config)
        for tex in self.header.textures:
            texName = array_to_str(tex.filename)
            if tex.type == 0:
                pass
            elif tex.type == 11:
                texName = rec.Texture1.value
            elif tex.type == 12:
                texName = rec.Texture2.value
            elif tex.type == 13:
                texName = rec.Texture3.value
            self.loadMaterials(texName)    
        
    def createSkins(self) -> []:
        self.skins.clear()
            
        # Meshes aus den Skin-Profilen erzeugen
        #for i in range(0,1): 
        for i in range(self.header.num_skin_profiles):
            skinName = f"{self.path}/{self.modelName}{i:02d}.skin"
        
            if(os.path.isfile(skinName) == False):
                # Datei ist nicht vorhanden
                break
        
            skin = M2SkinFile()
            skin.read(open(skinName, 'rb'))
            skin.draw_submesh(self)
            # Skin-File hinzufuegen
            self.skins.append(skin)
            
            
        return self.skins
    
    def createBones(self):
        """
            Erstellt die Bones fuer das aktuelle M2-Modell
        """

        
        self.key_bone_lookup_txt = ("ArmL", "ArmR", "ShoulderL", "ShoulderR", "Upper Body", "Waist", "Head", "Jaw", "IndexFingerR", 
                "MiddleFingerR", "PinkyFingerR", "RingFingerR", "ThumbR", "IndexFingerL", "MiddleFingerL", 
                "PinkyFingerL", "RingFingerL", "ThumbL", "$BTH", "$CSR", "$CSL", "_Breath", "_Name", "_NameMount", 
                "$CHD", "$CCH", "Root", "Wheel1", "Wheel2", "Wheel3", "Wheel4", "Wheel5", "Wheel6", "Wheel7", 
                "Wheel8", "FaceAttenuation", "CapeParent", "CapeChild1", "CapeChild2", "CapeChild3", "CapeChild4", 
                "TabardParent", "TabardChild1", "TabardChild2", "unk head top", "unk head top", "UpperBodyParent", 
                "NeckParent", "NeckChild1", "LowerBodyParent", "Buckle", "Chest", "Main", "LegR", "LegL", 
                "KneeR", "KneeL", "FootL", "FootR", "ElbowR", "ElbowL", "Unk_ElbowL_Child", "HandR", "HandL", 
                "WeaponR", "WeaponL", "Unk_WristL_Child", "Unk_WristR_Child", "KneeR_UpperRig", "KneeL_UpperRig", 
                "ArmR_2", "ArmL_2", "ElbowR_UpperRig", "ElbowL_UpperRig", "ForearmR", "ForearmL", "WristR_UpperRig", 
                "WristL_UpperRig")
        
        bpy.ops.object.mode_set(mode='EDIT') # Blender in Bearbeitungsmodus  
        ebs = self.arm.edit_bones
        
        # Liste der Blender-Bones
        self.eblist = []
        
        # Bones erzeugen
        print("Create Bones")
        for i in range(0, len(self.header.bones)):
            eb = ebs.new(self.getBoneName(i))
            self.eblist.append(eb)

        # Parent - Child Verhaeltnis        
        print("Verknuepfe Bones")
        self.bone_pairs = []
        for i in range(0, len(self.header.bones)):
            eb = self.eblist[i]
            b = self.header.bones[i]
            pivot = Vector()
            pivot = Vector(b.pivot)
            if b.parent_bone == -1:
                eb.head = pivot
                eb.tail = eb.head + Vector((0,0.01,0))
            else:
                eb.parent = self.eblist[b.parent_bone]
                eb.head = pivot
                eb.tail = eb.head + Vector((0,0.01,0))
                eb.use_inherit_rotation = True
                # Need to check for this because blender removes zero-length bones
                '''
                newbone = self.eblist[b.parent_bone].head - eb.head
                if newbone.length < 0.001:
                    self.eblist[b.parent_bone].tail = eb.head + Vector((0,0.1,0))
                else:
                    self.eblist[b.parent_bone].tail = eb.head
                '''
            self.bone_pairs.append(tuple([b, eb]))

        
        # Die Bones als Sticks darstellen
        self.arm.display_type = "STICK"
                    
    def getBoneName(self, bone_index):
        result = f"Bone_{bone_index:03d}"
        kb = self.header.key_bone_lookup
        kb_txt = self.key_bone_lookup_txt
        for i in range(0, len(kb)):
            if (kb[i] != 65535 and kb[i] == bone_index): 
                #result = kb_txt[i]
                result = result
        return result
                

    def loadMaterials(self, name):
        
        name = name.upper().removesuffix(".BLP")
        
        filename = self.base + "\\" + name + ".png"
        
        
        if not os.path.exists(filename) and not os.path.isfile(filename):
            filename = self.path + "\\" + name + ".png"

        if not os.path.exists(filename) and not os.path.isfile(filename):
            filename = self.archive + "\\" + name + ".png"

        if not os.path.exists(filename) and not os.path.isfile(filename):
            raise RuntimeError(f"Materialdatei {name} wurde nicht gefunden.")
        
        for ob in self.meshes:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            texImage.image = bpy.data.images.load(filename)
            mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

            #bpy.context.view_layer.objects.active = ob

            # Assign it to object
            ob.data.materials.append(mat)
    
    def save(self, obj):
        bpy.context.scene.objects.active = obj
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        #bpy.context.scene.objects.link(new_obj)
        bpy.context.scene.objects.active = new_obj
        
        mesh = new_obj.data
        original_mesh = obj.data
        
        
class M2SkinFile:
    def __init__(self):
        self.skin = M2SkinProfile()

    def read(self, f):        
        self.skin.read(f)

    def draw_submesh(self, m2_file):
        
        self.eblist = m2_file.eblist
        self.arm = m2_file.arm
        self.rig = m2_file.rig

        
        
        # Create the blender armature and object
        self.scene = m2_file.scene
        
        bpy.ops.object.mode_set(mode='OBJECT') # Blender in Objekt-Modus
        for submesh_index, submesh in enumerate(self.skin.submeshes):
            #print("  Creation of the submesh '%s'..." % submesh.name)

            # Create the blender mesh and object
            name = f"{m2_file.modelName}.Mesh.{submesh_index:03d}"                    
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            obj.location = (0, 0, 0)
            m2_file.meshes.append(obj)
            
            # Link the object to the scene
            self.scene.collection.objects.link(obj)
            #scene.objects.active = obj
            #scene.update()

            # Retrieve the triangles of the submesh
            print("    - %s triangles, from %d" % (submesh.nTriangles, submesh.StartTriangle))
            submesh_triangles = self.skin.triangles[submesh.StartTriangle:submesh.StartTriangle+submesh.nTriangles]
                
            # Retrieve the indices of the submesh
            print("    - %s indices, from %d" % (submesh.nVertices, submesh.StartVertex))
            submesh_indices = self.skin.indices[submesh.StartVertex:submesh.StartVertex+submesh.nVertices]
            # Retrieve the list of vertex coordinates
            submesh_vertices = [ m2_file.header.vertices[index] for index in submesh_indices ]
            
            verts = [ vertex.pos.to_tuple() for vertex in submesh_vertices ]
            for i in range(len(verts)):
                # von m2 zu normal
                vec = Vector(verts[i])
                verts[i] = vec.to_tuple()
                print("")
                

            # Retrieve the list of faces
            faces = list(map(lambda x: x.to_tuple(offset=submesh.StartVertex), submesh_triangles))
            
            
            # Create the mesh
            mesh.from_pydata(verts, [], faces)

            # Update the mesh with the new data
            mesh.update(calc_edges=True)

            # Normals
            for n, vertex in enumerate(mesh.vertices):
                vertex.normal = submesh_vertices[n].normal
            
            uv1 = mesh.uv_layers.new(name="UVMap")
            uv_layer1 = mesh.uv_layers[0]
            for i in range(len(uv_layer1.data)):
                uv = submesh_vertices[mesh.loops[i].vertex_index].tex_coords
                uv_layer1.data[i].uv = (uv[0], 1 - uv[1])
            
            uv1.active = True
            
            bones = []
            bone_groups = {}
            submesh_bone_table = m2_file.header.bone_lookup_table[submesh.StartBones:submesh.StartBones+submesh.nBones]
            
            
            for bone_index in submesh_bone_table:
                # bones.insert(bone_index, m2_file.header.bones[bone_index])
                bones.insert(bone_index, self.eblist[bone_index])
                bone_groups[bone_index] = []
                #group_names[bone_index] = self.eblist[bone_index].name
                        
            for vertex_index, vertex in enumerate(submesh_vertices):
                for n, bone_index in enumerate(vertex.bone_indices):
                    if bone_index > 0:
                        bone_groups[bone_index].append((vertex_index, vertex.bone_weights[n] / 255))

            for bone_index in bone_groups.keys():
                txt = m2_file.getBoneName(bone_index)
                grp = obj.vertex_groups.new(name=txt)
                for (v, w) in bone_groups[bone_index]:
                    grp.add([v], w, "REPLACE")           
                    
            obj.parent = self.rig
            modifier = obj.modifiers.new(type='ARMATURE', name=self.arm.name)
            modifier.object = self.rig  
            
                