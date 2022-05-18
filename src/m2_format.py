import sys
import struct
from mathutils import Vector, Matrix, Quaternion, Euler
import math
import mathutils



'''
class M2Loop:
    def __init__(self):
        self.timestamp = 0

    def Read(self, f):
        self.timestamp = struct.unpack("I", f.read(4))[0]

    def Write(self, f):
        f.write(struct.pack('I', self.timestamp))
'''

class C3Vector(Vector):       

    def read(self, f):
        self.x = struct.unpack("f",f.read(4))[0]
        self.y = struct.unpack("f",f.read(4))[0]
        self.z = struct.unpack("f",f.read(4))[0]


    def write(self, f):
        f.write(struct.pack("f",self.x))
        f.write(struct.pack("f",self.y))
        f.write(struct.pack("f",self.z))

class M2SplineKeyFloat:
    def read(self,f):
        self.value = struct.unpack("f",f.read(4))[0]

    def write(self, f):
        f.write(struct.pack("f",self.value))

class M2SplineKeyVectors(list):
    def __init__(self):
        super().__init__()
        self.append(C3Vector( (0, 0, 0)));
        self.append(C3Vector( (0, 0, 0)));
        self.append(C3Vector( (0, 0, 0)));

    def read(self,f):
        self[0].read(f)
        self[1].read(f)
        self[2].read(f)

    def write(self, f):
        self[0].write(f)
        self[1].write(f)
        self[2].write(f)
        
class M2CompQuat:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.w = 0
    
    def read(self,f):
        def MakeFloat(v):
#            return float(v / 32767.0) - 1.0; 
            v = float(v)
            f = float(0)
            if v > 0:
                f = float(v - 32767)
            else:
                f = float(v + 32767)

            return float(f / 32767.0)
        
        self.x = struct.unpack("h",f.read(2))[0]
        self.y = struct.unpack("h",f.read(2))[0]
        self.z = struct.unpack("h",f.read(2))[0]
        self.w = struct.unpack("h",f.read(2))[0]
        
        self.x = MakeFloat(self.x)
        self.y = MakeFloat(self.y)
        self.z = MakeFloat(self.z)
        self.w = MakeFloat(self.w)

    def write(self, f):
        f.write(struct.pack("h",self.x))
        f.write(struct.pack("h",self.y))
        f.write(struct.pack("h",self.z))
        f.write(struct.pack("h",self.w))
    

    def to_angles(self):
        angles = [0, 0, 0]
        w = self.w
        x = self.x
        y = self.y
        z = self.z
        sqw = float(w * w)
        sqx = float(x * x)
        sqy = float(y * y)
        sqz = float(z * z)
        unit = float(sqx + sqy + sqz + sqw) # if normalized is one, otherwise is correction factor
        test = float(x * y + z * w)
        if (test > 0.499 * unit):  
            # singularity at north pole
            angles[1] = 2 * math.atan2(x, w)
            angles[2] = math.pi/2
            angles[0] = 0
        elif (test < -0.499 * unit): 
            # singularity at south pole
            angles[1] = -2 * math.atan2(x, w)
            angles[2] = -1 * math.pi / 2
            angles[0] = 0
        else:
            angles[1] = math.atan2(2 * y * w - 2 * x * z, sqx - sqy - sqz + sqw) # roll or heading 
            angles[2] = math.asin(2 * test / unit) # pitch or attitude
            angles[0] = math.atan2(2 * x * w - 2 * y * z, -sqx + sqy - sqz + sqw) # yaw or bank
        return angles
    
    def __str__(self):
        msg = f"M2CompQuat(x={self.x}, y={self.y}, z={self.z}, w={self.w})"
        return msg

class CAaBox:
    def __init__(self):
        self.min = C3Vector( (0, 0, 0) )
        self.max = C3Vector( (0, 0, 0) )

    def read(self, f):
        self.min.read(f)
        self.max.read(f)
        
    def write(self, f):
        f.write(struct.pack('fff', self.min.x, self.min.y, self.min.z))
        f.write(struct.pack('fff', self.max.x, self.max.y, self.max.z))

class M2Array(list):
    number: int
    offset: int
    type: str
    def __init__(self):
        super().__init__()
        self.number    = 0
        self.offset    = 0
        self.type      = ''
    
    def read(self,f):
        self.number    = struct.unpack("i",f.read(4))[0]
        self.offset    = struct.unpack("i",f.read(4))[0]       
    
    def fill(self,f,m2_type,type2 = "I"):
        if (self.number == 0): return 
        self.type = m2_type
        oldpos = f.tell()
        f.seek(self.offset)
        if(m2_type == "M2Array"):
            for i in range(0, self.number):
                self.append(M2Array())
                self[i].read(f)
                self[i].fill(f, type2)
        elif(len(m2_type) == 1):            
            for i in range(0, self.number):
                self.append(struct.unpack(m2_type,f.read(struct.calcsize(m2_type)))[0])
        else:
            for i in range(0, self.number):
                self.append(getattr(sys.modules[__name__], m2_type)())
                self[i].read(f)
        f.seek(oldpos)
    
    def write(self, f):
        self.number = len[self]
    
        f.write(struct.pack("2i",self.number,self.offset))
        
        oldpos = f.tell()
        f.seek(self.offset)
        if(self.type == "M2Array"):
            for i in range(0, self.number):
                #self[i].offset Ã�Å¸Ã�Â Ã�ËœÃ�â€�Ã�Â£Ã�Å“Ã�ï¿½Ã�Â¢Ã�Â¬ Ã�Å¡Ã�ï¿½Ã�Å¡ Ã�Å¸Ã�ËœÃ�Â¡Ã�ï¿½Ã�Â¢Ã�Â¬ Ã�â€™ Ã�Å¡Ã�Å¾Ã�ï¿½Ã�â€¢Ã�Â¦ Ã�Â¤Ã�ï¿½Ã�â„¢Ã�â€ºÃ�ï¿½ (Ã�Å¸Ã�Â Ã�â€¢Ã�â€�Ã�â€™Ã�ï¿½Ã�Â Ã�ËœÃ�Â¢Ã�â€¢Ã�â€ºÃ�Â¬Ã�ï¿½Ã�Â«Ã�â„¢ Ã�Â Ã�ï¿½Ã�Â¡Ã�Â¡Ã�Â§Ã�ï¿½Ã�Â¢ Ã�Â Ã�ï¿½Ã�â€”Ã�Å“Ã�â€¢Ã�Â Ã�ï¿½?)
                self[i].write(f)
        elif(len(self.type) == 1):            
            for i in range(0, self.number):
                f.write(struct.pack(self.type, self[i]))
        else:
            for i in range(0, self.number):
                self[i].write(f)
        f.seek(oldpos)

class M2TrackBase:
    def __init__(self):
        self.interpolation_type = 0
        self.global_sequence    = -1
        self.timestamps         = M2Array()

    def read(self, f):
        self.interpolation_type = struct.unpack("H", f.read(2))[0]
        self.global_sequence = struct.unpack("h", f.read(2))[0]
        
        self.timestamps.read(f)
        self.timestamps.fill(f,"M2Array","I")
        
    def write(self, f):
        f.write(struct.pack('H', self.interpolation_type))
        f.write(struct.pack('h', self.global_sequence))
        
        self.timestamps.write(f)
        
class M2Track(M2TrackBase):
    def __init__(self):
        super().__init__()
        self.values = M2Array()

    def read(self, f, type):
        self.interpolation_type = struct.unpack("H", f.read(2))[0]
        self.global_sequence = struct.unpack("h", f.read(2))[0]
        
        self.timestamps.read(f)
        self.timestamps.fill(f,"M2Array","I")
        
        self.values.read(f)
        self.values.fill(f,"M2Array",type)
        
    def write(self, f):
        f.write(struct.pack('H', self.interpolation_type))
        f.write(struct.pack('h', self.global_sequence))
        
        self.timestamps.write(f)
        self.values.write(f)
    
    def getFrameNumber(self, animationSequence, time): 
        '''
        Returns the frame index that should be used for a given animation sequence
        and time. If the given time value is not valid, -1 is returned. Invalid
        times can be caused by timelines that have no data or where the time is
        longer than the actual length of the animation time.

        @param animationSequence
            Which animation sequence to use.
        @param time
            The time

         @return The frame index for the given time. If there is no timeline or the
                 given time goes beyond the length of the animation, than -1 is
                 returned.
         '''
        #
        # Start advancing through the timeline data until we've reached the frame
        # that we're supposed to be on. The frame we're on is the first frame
        # who's time value is greater than the current time that we're searching
        # for.
        #
        frame = 0
        times = self.getTimelineTimes(animationSequence)
        if (times == None):
            return -1
        
        if (len(times) == 0):
            return -1
        
        while (frame < len(times) and times[frame] <= time):
            frame+=1;
        
        if frame <= len(times):
            return frame -1
        else:
            return -1
    
     
    def getTimelineTimes(self, animationSequence):
        if (self.timestamps == None or animationSequence < 0 or animationSequence >= len(self.timestamps)):
            return None
        
        return self.timestamps[animationSequence];
    
    def getKeyFrameDataValue(self, animationSequence, time):
        '''
        Returns the data value used for a particular animation sequence and time.
        @param animationSequence
        @param time

        @return
        '''
        #
        # Do we have any data to return, and, if so, is the animation sequence
        # valid?
        #
        if (self.values == None or animationSequence < 0 or animationSequence >= len(self.values)):
            return None
        
        #
        # Get the frame number for this animation.
        #
        frame = self.getFrameNumber(animationSequence, time);
        if (frame == -1):
            return None
        
        #
        # Interpolate the data from the current frame to the next frame.
        #
        interpolate = False
        if (interpolate) :
            t1 = self.timestamps[animationSequence][frame]
            t2 = self.timestamps[animationSequence][frame + 1]
            if (t2 - t1 != 0):
                r = float(time - t1) / float(t2 - t1)

                if (self.interpolation_type == 1):
                    return self.interpolate(self.values[animationSequence][frame], self.values[animationSequence][frame + 1], r)

        return self.values[animationSequence][frame];

        
class M2Sequence:
    def __init__(self):
        self.animation_id        = 0
        self.sub_animation_id    = 0
        self.length              = 0
        self.moving_speed        = 0
        self.flags               = 0
        self.probability         = 0
        self.padding             = 0
        self.minimum_repetitions = 0
        self.maximum_repetitions = 0
        self.blend_time          = 0
        self.bounds              = CAaBox()
        self.bound_radius        = 0
        self.next_animation      = 0
        self.aliasNext           = 0   
        self.size                = 64
        
    def read(self, f):
        self.animation_id        = struct.unpack("H", f.read(2))[0]
        self.sub_animation_id    = struct.unpack("H", f.read(2))[0]
        self.length              = struct.unpack("I", f.read(4))[0]
        self.moving_speed        = struct.unpack("f", f.read(4))[0]
        self.flags               = struct.unpack("I", f.read(4))[0]
        self.probability         = struct.unpack("h", f.read(2))[0]
        self.padding             = struct.unpack("H", f.read(2))[0]
        self.minimum_repetitions = struct.unpack("I", f.read(4))[0]
        self.maximum_repetitions = struct.unpack("I", f.read(4))[0]
        self.blend_time          = struct.unpack("I", f.read(4))[0]
        self.bounds              = self.bounds.read(f)
        self.bound_radius        = struct.unpack("f", f.read(4))[0]
        self.next_animation      = struct.unpack("h", f.read(2))[0]
        self.aliasNext           = struct.unpack("H", f.read(2))[0] 

    def write(self, f):
        f.write(struct.pack('H', self.animation_id))
        f.write(struct.pack('H', self.sub_animation_id))
        f.write(struct.pack('I', self.length))
        f.write(struct.pack('f', self.moving_speed))
        f.write(struct.pack('I', self.flags))
        f.write(struct.pack('h', self.probability))
        f.write(struct.pack('H', self.padding))
        f.write(struct.pack('I', self.minimum_repetitions))
        f.write(struct.pack('I', self.maximum_repetitions))
        f.write(struct.pack('I', self.blend_time))
        self.bounds.Write(f)
        f.write(struct.pack('f', self.bound_radius))
        f.write(struct.pack('h', self.next_animation))
        f.write(struct.pack('H', self.aliasNext))

class M2CompBone:
    FLAG_IGNORE_PARENT_TRANSLATE = 0x1
    FLAG_IGNORE_PARENT_SCALE = 0x2
    FLAG_IGNORE_PARENT_ROTATION = 0x4
    FLAG_SPHERICAL_BILLBOARD = 0x8
    FLAG_CYLINDRICAL_BILLBOARD_LOCK_X = 0x10
    FLAG_CYLINDRICAL_BILLBOARD_LOCK_Y = 0x20
    FLAG_CYLINDRICAL_BILLBOARD_LOCK_Z = 0x40
    FLAG_TRANSFORMED = 0x200
    FLAG_KINEMATIC_BONE = 0x400       # MoP+: allow physics to influence this bone
    FLAG_HELMET_ANIM_SCALED = 0x1000  # set blend_modificator to helmetAnimScalingRec.m_amount for this bone
    FLAG_SOMETHING_SEQUENCE_ID = 0x2000 # <=bfa+, parent_bone+submesh_id are a sequence id instead?!
    
    key_bone_id : int
    flags       : int
    parent_bone : int
    submesh_id  : int
    translation : M2Track
    rotation    : M2Track
    scale       : M2Track
    pivot       : C3Vector
    
    lastCalcMatrix : Matrix
    lastTranslation: Vector
    lastRotation   : Quaternion
    lastScaling    : Vector
    
    def __init__(self):
        self.key_bone_id = 0
        self.flags       = 0
        self.parent_bone = 0
        self.submesh_id  = 0
        self.unk         = (0,0)
        self.translation = M2Track()
        self.rotation    = M2Track()
        self.scale       = M2Track()
        self.pivot       = C3Vector( (0,0,0) )
        self.size        = 88

    def read(self, f):
        self.key_bone_id = struct.unpack("i", f.read(4))[0]
        self.flags = struct.unpack("I", f.read(4))[0]
        self.parent_bone = struct.unpack("h", f.read(2))[0]
        self.submesh_id = struct.unpack("H", f.read(2))[0]
        self.unk = struct.unpack("HH", f.read(4))
        self.translation.read(f,"C3Vector")
        self.rotation.read(f,"M2CompQuat")
        self.scale.read(f,"C3Vector")
        self.pivot.read(f)

    def write(self, f):
        f.write(struct.pack('i', self.key_bone_id))
        f.write(struct.pack('I', self.flags))
        f.write(struct.pack('h', self.parent_bone))
        f.write(struct.pack('H', self.submesh_id))
        f.write(struct.pack('HH', *self.unk))
        self.translation.write(f,"C3Vector")
        self.rotation.write(f,"M2CompQuat")
        self.scale.write(f,"C3Vector")
        self.pivot.write(f)
    
    def calculateMatrixJme(self, animationSequence, time) -> Matrix:
        '''
        Calculate the matrix for a given animation sequence and time.
        
        @param animationSequence
        The animation sequence to calculate the matrix for.
        @param time
        The time into the animation sequence.
        
        @return
        '''
        def mult(in1, in2, store = None):
            if (store == None):
                store = mathutils.Matrix().to_4x4()

            temp00 = in1[0][0] * in2[0][0] + in1[0][1] * in2[1][0] + in1[0][2] * in2[2][0] + in1[0][3] * in2[3][0]
            temp01 = in1[0][0] * in2[0][1] + in1[0][1] * in2[1][1] + in1[0][2] * in2[2][1] + in1[0][3] * in2[3][1]
            temp02 = in1[0][0] * in2[0][2] + in1[0][1] * in2[1][2] + in1[0][2] * in2[2][2] + in1[0][3] * in2[3][2]
            temp03 = in1[0][0] * in2[0][3] + in1[0][1] * in2[1][3] + in1[0][2] * in2[2][3] + in1[0][3] * in2[3][3]
        
            temp10 = in1[1][0] * in2[0][0] + in1[1][1] * in2[1][0] + in1[1][2] * in2[2][0] + in1[1][3] * in2[3][0]
            temp11 = in1[1][0] * in2[0][1] + in1[1][1] * in2[1][1] + in1[1][2] * in2[2][1] + in1[1][3] * in2[3][1]
            temp12 = in1[1][0] * in2[0][2] + in1[1][1] * in2[1][2] + in1[1][2] * in2[2][2] + in1[1][3] * in2[3][2]
            temp13 = in1[1][0] * in2[0][3] + in1[1][1] * in2[1][3] + in1[1][2] * in2[2][3] + in1[1][3] * in2[3][3]

            temp20 = in1[2][0] * in2[0][0] + in1[2][1] * in2[1][0] + in1[2][2] * in2[2][0] + in1[2][3] * in2[3][0]
            temp21 = in1[2][0] * in2[0][1] + in1[2][1] * in2[1][1] + in1[2][2] * in2[2][1] + in1[2][3] * in2[3][1]
            temp22 = in1[2][0] * in2[0][2] + in1[2][1] * in2[1][2] + in1[2][2] * in2[2][2] + in1[2][3] * in2[3][2]
            temp23 = in1[2][0] * in2[0][3] + in1[2][1] * in2[1][3] + in1[2][2] * in2[2][3] + in1[2][3] * in2[3][3]
            
            temp30 = in1[3][0] * in2[0][0] + in1[3][1] * in2[1][0] + in1[3][2] * in2[2][0] + in1[3][3] * in2[3][0]
            temp31 = in1[3][0] * in2[0][1] + in1[3][1] * in2[1][1] + in1[3][2] * in2[2][1] + in1[3][3] * in2[3][1]
            temp32 = in1[3][0] * in2[0][2] + in1[3][1] * in2[1][2] + in1[3][2] * in2[2][2] + in1[3][3] * in2[3][2]
            temp33 = in1[3][0] * in2[0][3] + in1[3][1] * in2[1][3] + in1[3][2] * in2[2][3] + in1[3][3] * in2[3][3]
        
            store[0][0] = temp00
            store[0][1] = temp01
            store[0][2] = temp02
            store[0][3] = temp03
            store[1][0] = temp10
            store[1][1] = temp11
            store[1][2] = temp12
            store[1][3] = temp13
            store[2][0] = temp20
            store[2][1] = temp21
            store[2][2] = temp22
            store[2][3] = temp23
            store[3][0] = temp30
            store[3][1] = temp31
            store[3][2] = temp32
            store[3][3] = temp33
                
            return store
     
        didTranslation = False
        didRotation = False
        didScaling = False
        
        '''
            4x4 Matrix
        '''
        #m = Matrix.Translation((self.pivot.x, self.pivot.y, self.pivot.z)).to_4x4()
        m = Matrix.Translation((self.pivot.x, self.pivot.y, self.pivot.z))
        m = Matrix.Translation((0, 0, 0))
        
        
        #
        # Get the translation, rotation, and scaling vectors for the given
        # animation sequence and time.  These values will be interpolated between
        # the two frames that "surround" the time.
        #
        transVec = None
        rotQuat = None
        scaleVec = None
        val = self.translation.getKeyFrameDataValue(animationSequence, time)
        if val != None:
            transVec = Vector((val.x, val.y, val.z))
        
        val = self.rotation.getKeyFrameDataValue(animationSequence, time)
        if val != None:
            angles = val.to_angles()
            
            msg = f"M2CompQuat(w={val.w:.6f}, x={val.x:.6f}, y={val.y:.6f}, z={val.z:.6f})"
            #print(msg)
            msg = f"M2CompQuat(yaw={math.degrees(angles[0])}, roll={math.degrees(angles[1])}, pitch={math.degrees(angles[2])})"
            #print(msg)
            rotQuat = Quaternion((val.w, val.x, val.y, val.z))
            eul = rotQuat.to_euler("XZY")
            
            msg = f"CompQuat(yaw={math.degrees(eul[0])}, roll={math.degrees(angles[1])}, pitch={math.degrees(angles[2])})"
            #print(msg)
            
        val = self.scale.getKeyFrameDataValue(animationSequence, time)
        if val != None:
            scaleVec = Vector((val.x, val.y, val.z))

        #
        # Calculate the translation part of the animation.
        #
        if (transVec != None) :
            #
            # Set the translation for the matrix.
            ##
            #transMat = Matrix.Translation(transVec).to_4x4()
            transMat = Matrix.Translation(transVec)
            
            m = mult(m, transMat)
            #m = m @ transMat
            
            didTranslation = True
            self.lastTranslation = transVec
        else :
            self.lastTranslation = Vector();
        
        #
        # Calculate the rotation part of the animation. Get the rotation quaternion
        # for the given animation sequence.
        #
        if (rotQuat != None) :
            #
            # Get the rotation quaternion for this frame.
            #
            #rotMat = Matrix.Rotation(rotQuat.angle, 4, rotQuat.axis)
            rotMat = rotQuat.to_matrix().to_4x4()
            
            m = mult(m, rotMat)
            #m = m @ rotMat
            
            didRotation = True
            self.lastRotation = rotQuat
        else :
            self.lastRotation = Quaternion();

        #
        # Calculate the scaling part of the animation.
        #
        if (scaleVec != None) :
            if (scaleVec.x > 10) :
                scaleVec.x = 1.0

            if (scaleVec.y > 10) :
                scaleVec.y = 1.0

            if (scaleVec.z > 10) :
                scaleVec.z = 1.0

            #scaleMat = Matrix().to_4x4()
            scaleMat = Matrix().to_4x4()
            scaleMat = mult(scaleMat, Matrix.Scale(scaleVec.x, 4, Vector((1,0,0))))
            scaleMat = mult(scaleMat, Matrix.Scale(scaleVec.y, 4, Vector((0,1,0))))
            scaleMat = mult(scaleMat, Matrix.Scale(scaleVec.z, 4, Vector((0,0,1))))
            
            m = mult(m, scaleMat)
            #m = m @ scaleMat
            
            self.lastScaling = scaleVec
            didScaling = True
        else :
            self.lastScaling = Vector((1.0, 1.0, 1.0));

        #
        # If we didn't do anything, return a matrix set to an identity matrix.
        #
        if (didTranslation == False and didRotation == False and didScaling == False) :
            m = mathutils.Matrix().to_4x4()
        else :
            #
            # Finish up...
            #
            unpivot = Vector((-self.pivot.x, -self.pivot.y, -self.pivot.z))
            unpivot = Vector((0, 0, 0))

            #unpiv = Matrix.Translation(unpivot).to_4x4()
            unpiv = Matrix.Translation(unpivot)
            
            m = mult(m, unpiv)
            #m = m @ unpiv
            
        #
        # Save the matrix.
        #
        self.lastCalcMatrix = m;
        return m;        


class M2Vertex:
    # 0x00  float   Position[3]         A vector to the position of the vertex.
    # 0x0C  uint8   BoneWeight[4]       The vertex weight for 4 bones.
    # 0x10  uint8   BoneIndices[4]      Which are referenced here.
    # 0x14  float   Normal[3]           A normal vector.
    # 0x20  float   TextureCoords[2]    Coordinates for a texture.
    # 0x28  float   Unknown[2]          Null?

    FORMAT = "<fffBBBBBBBBfffffff"
    def __init__(self):
        self.pos            = C3Vector( (0, 0, 0) )
        self.bone_weights   = ( 0, 0, 0, 0 )
        self.bone_indices   = ( 0, 0, 0, 0 )
        self.normal         = C3Vector( (0, 0, 0) )
        self.tex_coords     = Vector( (0, 0) )
        self.unknown   = ( 0, 0 )
        self.size = 48

    def read(self, f):
        self.pos.read(f)
        self.bone_weights   = struct.unpack("BBBB", f.read(4))
        self.bone_indices   = struct.unpack("BBBB", f.read(4))
        self.normal.read(f)
        self.tex_coords     = Vector( struct.unpack("ff", f.read(8)) )
        self.unknown        = struct.unpack("ff", f.read(8))

    def write(self, f):
        f.write(struct.pack('fff', *self.pos))
        f.write(struct.pack('BBBB', *self.bone_weights))
        f.write(struct.pack('BBBB', *self.bone_indices))
        f.write(struct.pack('fff', *self.normal))
        f.write(struct.pack('ff', *self.tex_coords))

class M2Color:
    def __init__(self):
        self.color = M2Track()
        self.alpha = M2Track()
        self.size = 40
    def read(self, f):
        self.color.read(f,"C3Vector")
        
        self.alpha.read(f,"H")

    def write(self, f):
        self.color.write(f,"C3Vector")
        
        self.alpha.write(f,"H")

class M2Texture:
    type: int
    flags: int
    filename: M2Array
    size: int
    
    def __init__(self):
        self.type     = 0
        self.flags    = 0
        self.filename = M2Array()
        self.size = 16

    def read(self, f):
        self.type   = struct.unpack("I", f.read(4))[0]
        self.flags  = struct.unpack("I", f.read(4))[0]
        self.filename.read(f)
        self.filename.fill(f, "c")

    def write(self, f):
        f.write(struct.pack('I', self.type))
        f.write(struct.pack('I', self.flags))
        
        self.filename.write(f)
        
    def __str__(self):
        return f'M2Texture(type={self.type}, flags={self.flags}, filename={self.filename})'

class M2TextureWeight:
    weight: M2Track
    size: int
    
    def __init__(self):
        self.weight = M2Track()
        self.size = 20
    def read(self, f):
        self.weight.read(f, "H")

    def write(self, f):
        self.weight.write(f, "H")

class M2TextureTransform:
    def __init__(self):
        self.translation = M2Track()
        self.rotation    = M2Track()
        self.scaling     = M2Track()
        self.size = 60

    def read(self, f):
        self.translation.read(f,"C3Vector")
        self.rotation.read(f,"M2CompQuat")
        self.scaling.read(f,"C3Vector")

    def write(self, f):
        self.translation.write(f,"C3Vector")
        self.rotation.write(f,"M2CompQuat")
        self.scaling.write(f,"C3Vector")

class M2Material:
    def __init__(self):
        self.flags         = 0
        self.blending_mode = 0
        self.size = 4
    def read(self, f):
        self.type   = struct.unpack("H", f.read(2))[0]
        self.flags  = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack('H', self.type))
        f.write(struct.pack('H', self.flags))

class M2Attachment:
    def __init__(self):
        self.id               = 0
        self.bone             = 0
        self.unk              = 0
        self.position         = C3Vector( (0, 0, 0) )
        self.animate_attached = M2Track()
        self.size = 40

    def read(self, f):
        self.type   = struct.unpack("I", f.read(4))[0]
        self.bone  = struct.unpack("H", f.read(2))[0]
        self.unk  = struct.unpack("H", f.read(2))[0]
        self.position.read(f)
        self.animate_attached.read(f, "B")

    def write(self, f):
        f.write(struct.pack('I', self.type))
        f.write(struct.pack('H', self.bone))
        f.write(struct.pack('H', self.unk))
        self.position.write(f)
        self.animate_attached.write(f, "B")

class M2Event:
    def __init__(self):
        self.identifier = 0
        self.data       = 0
        self.bone       = 0
        self.position   = C3Vector( (0, 0, 0) )
        self.enabled    = M2TrackBase()
        self.size = 36

    def read(self, f):
        self.identifier   = struct.unpack("I", f.read(4))[0]
        self.data  = struct.unpack("I", f.read(4))[0]
        self.bone  = struct.unpack("I", f.read(4))[0]
        self.position.read(f)
        self.enabled.read(f)

    def write(self, f):
        f.write(struct.pack('I', self.identifier))
        f.write(struct.pack('I', self.data))
        f.write(struct.pack('I', self.bone))
        self.position.write(f)
        self.enabled.write(f)

class M2Light:
    def __init__(self):
        self.type              = 0
        self.bone              = 0
        self.position          = C3Vector( (0, 0, 0) )
        self.ambient_color     = M2Track()
        self.ambient_intensity = M2Track()
        self.diffuse_color     = M2Track()
        self.diffuse_intensity = M2Track()
        self.attenuation_start = M2Track()
        self.attenuation_end   = M2Track()
        self.visibility        = M2Track()
        self.size = 156

    def read(self, f):
        self.type   = struct.unpack("H", f.read(2))[0]
        self.bone  = struct.unpack("h", f.read(2))[0]
        self.position.read(f)
        self.ambient_color.read(f, "C3Vector")
        self.ambient_intensity.read(f, "f")
        self.diffuse_color.read(f, "C3Vector")
        self.diffuse_intensity.read(f, "f")
        self.attenuation_start.read(f, "f")
        self.attenuation_end.read(f, "f")
        self.visibility.read(f, "B")

    def write(self, f):
        f.write(struct.pack('H', self.type))
        f.write(struct.pack('h', self.bone))
        self.position.write(f)
        self.ambient_color.write(f, "C3Vector")
        self.ambient_intensity.write(f, "f")
        self.diffuse_color.write(f, "C3Vector")
        self.diffuse_intensity.write(f, "f")
        self.attenuation_start.write(f, "f")
        self.attenuation_end.write(f, "f")
        self.visibility.write(f, "B")

class M2Camera:
    def __init__(self):
        self.type                 = 0
        self.fov                  = 0
        self.far_clip             = 0
        self.near_clip            = 0
        self.positions            = M2Track()
        self.position_base        = C3Vector( (0, 0, 0) )
        self.target_position      = M2Track()
        self.target_position_base = C3Vector( (0, 0, 0) )
        self.roll                 = M2Track()
        self.size = 100

    def read(self, f):
        self.type   = struct.unpack("I", f.read(4))[0]
        self.fov  = struct.unpack("f", f.read(4))[0]
        self.far_clip = struct.unpack("f", f.read(4))[0]
        self.near_clip = struct.unpack("f", f.read(4))[0]
        self.positions.read(f, "M2SplineKeyVectors")
        self.position_base.read(f)
        self.target_position.read(f, "M2SplineKeyVectors")
        self.target_position_base.read(f)
        self.roll.read(f, "M2SplineKeyFloat")

    def write(self, f):
        f.write(struct.pack('I', self.type))
        f.write(struct.pack('f', self.fov))
        f.write(struct.pack('f', self.far_clip))
        f.write(struct.pack('f', self.near_clip))
        self.positions.write(f, "M2SplineKeyVectors")
        self.position_base.write(f)
        self.target_position.write(f, "M2SplineKeyVectors")
        self.target_position_base.write(f)
        self.roll.write(f, "C3Vector")

class M2Ribbon:
    def __init__(self):
        self.ribbonId          = 0
        self.boneIndex         = 0
        self.position          = C3Vector( (0, 0, 0) )
        self.texture_refs      = M2Array()
        self.blend_refs        = M2Array()
        self.color             = M2Track()
        self.opacity           = M2Track()
        self.height_above      = M2Track()
        self.height_below      = M2Track()
        self.edgesPerSec       = 0
        self.edgeLifeSpanInSec = 0
        self.gravity           = 0
        self.m_rows            = 0
        self.m_cols            = 0
        self.texSlotTrack      = M2Track()
        self.visibilityTrack   = M2Track()
        self.priorityPlane     = 0
        self.padding           = 0
        self.size = 176

    def read(self, f):
        self.ribbonId   = struct.unpack("I", f.read(4))[0]
        self.boneIndex   = struct.unpack("I", f.read(4))[0]
        self.position.read(f)
        
        self.texture_refs.read(f)
        self.texture_refs.fill(f, "H")
        self.blend_refs.read(f)
        self.blend_refs.fill(f, "H")
        
        self.color.read(f, "C3Vector")
        self.opacity.read(f, "H")
        self.height_above.read(f, "f")
        self.height_below.read(f, "f")
        
        self.edgesPerSec   = struct.unpack("f", f.read(4))[0]
        self.edgeLifeSpanInSec   = struct.unpack("f", f.read(4))[0]
        self.gravity   = struct.unpack("f", f.read(4))[0]
        self.m_rows   = struct.unpack("H", f.read(2))[0]
        self.m_cols   = struct.unpack("H", f.read(2))[0]
        
        self.texSlotTrack.read(f, "H")
        self.visibilityTrack.read(f, "B")
        
        self.priorityPlane   = struct.unpack("h", f.read(4))[0]
        self.padding   = struct.unpack("H", f.read(4))[0]
    def write(self, f):
        f.write(struct.pack('I', self.ribbonId))
        f.write(struct.pack('I', self.boneIndex))    

        self.position.write(f)
        
        self.texture_refs.write(f)
        #self.texture_refs.fill(f, "H")
        self.blend_refs.write(f)
        #self.blend_refs.fill(f, "H")
        
        self.color.write(f, "C3Vector")
        self.opacity.write(f, "H")
        self.height_above.write(f, "f")
        self.height_below.write(f, "f")       

        f.write(struct.pack('f', self.edgesPerSec))
        f.write(struct.pack('f', self.edgeLifeSpanInSec))   
        f.write(struct.pack('f', self.gravity))
        f.write(struct.pack('H', self.m_rows))   
        f.write(struct.pack('H', self.m_cols))
        
        self.texSlotTrack.write(f, "H")
        self.visibilityTrack.write(f, "B")
        
        f.write(struct.pack('h', self.priorityPlane))
        f.write(struct.pack('H', self.padding)) 
        
class M2Header:
    FORMAT = "<IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIffffffffffffffIIIIIIIIIIIIIIIIIIIIII"
    def __init__(self):
        self.magic                           = 0
        self.version                         = 0
        self.name                            = M2Array()
        self.globalFlags                     = 0
        self.global_loops                    = M2Array()
        self.sequences                       = M2Array()
        self.sequence_lookups                = M2Array()
        self.bones                           = M2Array()
        self.key_bone_lookup                 = M2Array()
        self.vertices                        = M2Array()
        # Anzahl der Skin-Profile
        self.num_skin_profiles               = 0
        self.colors                          = M2Array()
        self.textures                        = M2Array()
        self.texture_weights                 = M2Array()
        self.texture_transforms              = M2Array()
        self.replacable_texture_lookup       = M2Array()
        self.materials                       = M2Array()
        self.bone_lookup_table               = M2Array()
        self.texture_lookup_table            = M2Array()
        self.tex_unit_lookup_table           = M2Array()
        self.transparency_lookup_table       = M2Array()
        self.texture_transforms_lookup_table = M2Array()
        self.bounding_box                    = CAaBox()
        self.bounding_sphere_radius          = 0
        self.collision_box                   = CAaBox()
        self.collision_sphere_radius         = 0
        self.collision_triangles             = M2Array()
        self.collision_vertices              = M2Array()
        self.collision_normals               = M2Array()
        self.attachments                     = M2Array()
        self.attachment_lookup_table         = M2Array()
        self.events                          = M2Array()
        self.lights                          = M2Array()
        self.cameras                         = M2Camera()
        self.camera_lookup_table             = M2Array()
        self.ribbon_emitters                 = M2Array()
        self.particle_emitters               = M2Array()
        self.blend_map_overrides             = M2Array()


    def read(self, f):
        self.magic = struct.unpack("I", f.read(4))[0]
        print("Read Magic: Done!")
        
        self.version = struct.unpack("I", f.read(4))[0]
        print("Read Version: Done!")
        
        self.name.read(f)
        self.name.fill(f, "c")
        print("Read Name: Done!")
        
        self.globalFlags = struct.unpack("I", f.read(4))[0]
        print("Read Global Flags: Done!")

        self.global_loops.read(f)
        self.global_loops.fill(f, "I")
        print("Read Global Loops: Done!")
        
        self.sequences.read(f)
        self.sequences.fill(f, "M2Sequence")
        print("Read Sequences: Done!")
        
        self.sequence_lookups.read(f)
        self.sequence_lookups.fill(f, "H")
        print("Read Sequence Lookups: Done!")
        
        self.bones.read(f)
        self.bones.fill(f, "M2CompBone")
        self.bones.number
        print("Read Bones: Done!")
        
        self.key_bone_lookup.read(f)
        self.key_bone_lookup.fill(f, "H")
        
        self.vertices.read(f)
        self.vertices.fill(f, "M2Vertex")
        
        self.num_skin_profiles = struct.unpack("I", f.read(4))[0]
        
        self.colors.read(f)
        self.colors.fill(f, "M2Color")
        print("Color")
        
        self.textures.read(f)
        self.textures.fill(f, "M2Texture")
        
        self.texture_weights.read(f)
        self.texture_weights.fill(f, "M2TextureWeight")
        
        self.texture_transforms.read(f)
        self.texture_transforms.fill(f, "M2TextureTransform")
        
        self.replacable_texture_lookup.read(f)
        self.replacable_texture_lookup.fill(f, "H")
        
        self.materials.read(f)
        self.materials.fill(f, "M2Material")
        
        self.bone_lookup_table.read(f)
        self.bone_lookup_table.fill(f, "H")
        
        self.texture_lookup_table.read(f)
        self.texture_lookup_table.fill(f, "H")
        
        self.tex_unit_lookup_table.read(f)
        self.tex_unit_lookup_table.fill(f, "H")
        
        self.transparency_lookup_table.read(f)
        self.transparency_lookup_table.fill(f, "H")
        
        self.texture_transforms_lookup_table.read(f)
        self.texture_transforms_lookup_table.fill(f, "H")
        
        self.bounding_box.read(f)
        self.bounding_sphere_radius = struct.unpack("f", f.read(4))[0]
        self.collision_box.read(f)
        self.collision_sphere_radius = struct.unpack("f", f.read(4))[0]
        
        self.collision_triangles.read(f)
        self.collision_triangles.fill(f, "H")
        
        self.collision_vertices.read(f)
        self.collision_vertices.fill(f, "C3Vector")
        
        self.collision_normals.read(f)
        self.collision_normals.fill(f, "C3Vector")
        
        self.attachments.read(f)
        self.attachments.fill(f, "M2Attachment")
        
        self.attachment_lookup_table.read(f)
        self.attachment_lookup_table.fill(f, "H")
        
        self.events.read(f)
        self.events.fill(f, "M2Event")
        
        self.lights.read(f)
        self.lights.fill(f, "M2Light")
        print("Light")
        
#        self.cameras.read(f)
#        self.cameras.fill(f, "M2Camera")
        
#        self.camera_lookup_table.read(f)
#        self.camera_lookup_table.fill(f, "H")
        
#        self.ribbon_emitters.read(f)
#        self.ribbon_emitters.fill(f, "M2Ribbon")
        
        #self.particle_emitters.read(f)
        #self.particle_emitters.fill(f, "M2Particle")
        
        #self.blend_map_overrides.read(f)
        #self.blend_map_overrides.fill(f, "H")
    def write(self, f):
        f.write(struct.pack('fff', *self.position))
        f.write(struct.pack('BBBB', *self.bone_weights))
        f.write(struct.pack('BBBB', *self.bone_indices))
        f.write(struct.pack('fff', *self.normal))
        f.write(struct.pack('ff', *self.texture_coords))

class M2Property(list):
    def __init__(self):
        super().__init__()
        self.append(0);
        self.append(0);
        self.append(0);
        self.append(0);

    def read(self,f):
        self[0] = struct.unpack("B", f.read(1))[0]
        self[1] = struct.unpack("B", f.read(1))[0]
        self[2] = struct.unpack("B", f.read(1))[0]
        self[3] = struct.unpack("B", f.read(1))[0]

    def write(self, f):
        f.write(struct.pack("B",self[0]))
        f.write(struct.pack("B",self[1]))
        f.write(struct.pack("B",self[2]))
        f.write(struct.pack("B",self[3]))

class M2Triangle(list):
    def __init__(self):
        super().__init__()
        self.append(0);
        self.append(0);
        self.append(0);

    def read(self,f):
        self[0] = struct.unpack("H", f.read(2))[0]
        self[1] = struct.unpack("H", f.read(2))[0]
        self[2] = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack("H",self[0]))
        f.write(struct.pack("H",self[1]))
        f.write(struct.pack("H",self[2]))
        
    def to_tuple(self, offset=0):
        return (self[0] - offset, self[1] - offset, self[2] - offset) 
        
class M2SkinSection:
    def __init__(self):
        self.SubmeshID         = 0
        self.Level             = 0
        self.StartVertex       = 0
        self.nVertices         = 0
        self.StartTriangle     = 0
        self.nTriangles        = 0
        self.nBones            = 0
        self.StartBones        = 0
        self.boneInfluences    = 0
        self.RootBone          = 0
        self.CenterMass        = C3Vector( (0, 0, 0) )
        self.CenterBoundingBox = C3Vector( (0, 0, 0) )
        self.Radius            = 0
        
    def read(self, f):
        self.SubmeshID   = struct.unpack("H", f.read(2))[0]
        self.Level   = struct.unpack("H", f.read(2))[0]
        self.StartVertex   = struct.unpack("H", f.read(2))[0]
        self.nVertices   = struct.unpack("H", f.read(2))[0]
        self.StartTriangle   = struct.unpack("H", f.read(2))[0] // 3
        self.nTriangles   = struct.unpack("H", f.read(2))[0] // 3
        self.nBones   = struct.unpack("H", f.read(2))[0]
        self.StartBones   = struct.unpack("H", f.read(2))[0]
        self.boneInfluences   = struct.unpack("H", f.read(2))[0]
        self.RootBone   = struct.unpack("H", f.read(2))[0]
        self.CenterMass.read(f)
        self.CenterBoundingBox.read(f)
        self.Radius   = struct.unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack("H",self.SubmeshID))
        f.write(struct.pack("H",self.Level))
        f.write(struct.pack("H",self.StartVertex))
        f.write(struct.pack("H",self.nVertices))
        f.write(struct.pack("H",self.StartTriangle))
        f.write(struct.pack("H",self.nTriangles))
        f.write(struct.pack("H",self.nBones))
        f.write(struct.pack("H",self.StartBones))
        f.write(struct.pack("H",self.boneInfluences))
        f.write(struct.pack("H",self.RootBone))
        self.CenterMass.write(f)
        self.CenterBoundingBox.write(f)
        f.write(struct.pack("f",self.Radius))
        

class M2Batch:
    def __init__(self):
        self.flags            = 0
        self.shader_id        = 0
        self.submesh_index    = 0
        self.submesh_index2   = 0
        self.color_index      = 0
        self.render_flags     = 0
        self.layer            = 0
        self.op_count         = 0
        self.texture          = 0
        self.tex_unit_number2 = 0
        self.transparency     = 0
        self.texture_anim     = 0
      
    def read(self, f):
        self.flags   = struct.unpack("H", f.read(2))[0]
        self.shader_id   = struct.unpack("H", f.read(2))[0]
        self.submesh_index   = struct.unpack("H", f.read(2))[0]
        self.submesh_index2   = struct.unpack("H", f.read(2))[0]
        self.color_index   = struct.unpack("h", f.read(2))[0]
        self.render_flags   = struct.unpack("H", f.read(2))[0]
        self.layer   = struct.unpack("H", f.read(2))[0]
        self.op_count   = struct.unpack("H", f.read(2))[0]
        self.texture   = struct.unpack("H", f.read(2))[0]
        self.tex_unit_number2   = struct.unpack("H", f.read(2))[0]
        self.transparency   = struct.unpack("H", f.read(2))[0]
        self.texture_anim   = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack("H",self.flags))
        f.write(struct.pack("H",self.shader_id))
        f.write(struct.pack("H",self.submesh_index))
        f.write(struct.pack("H",self.submesh_index2))
        f.write(struct.pack("h",self.color_index))
        f.write(struct.pack("H",self.render_flags))
        f.write(struct.pack("H",self.layer))
        f.write(struct.pack("H",self.op_count))
        f.write(struct.pack("H",self.texture))
        f.write(struct.pack("H",self.tex_unit_number2))
        f.write(struct.pack("H",self.transparency))
        f.write(struct.pack("H",self.texture_anim))
        
class M2SkinProfile:
    def __init__(self):
        self.magic         = 0
        self.indices       = M2Array()
        self.triangles     = M2Array()
        self.properties    = M2Array()
        self.submeshes     = M2Array()
        self.texture_units = M2Array()
        self.bones         = 0
        
    def read(self, f):
        self.magic   = struct.unpack("I", f.read(4))[0]
        
        self.indices.read(f)
        self.indices.fill(f, "H")
        
        self.triangles.read(f)
        self.triangles.number = self.triangles.number // 3
        self.triangles.fill(f, "M2Triangle")
        
        self.properties.read(f)
        self.properties.fill(f, "M2Property")
        
        self.submeshes.read(f)
        self.submeshes.fill(f, "M2SkinSection")
        
        self.texture_units.read(f)
        self.texture_units.fill(f, "M2Batch")
        
        self.bones   = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack("I",self.magic))
        self.triangles.write(f)
        #self.triangles.fill(f, "M2Triangle")
        
        self.properties.write(f)
        #self.properties.fill(f, "M2Property")
        
        self.submeshes.write(f)
        #self.submeshes.fill(f, "M2SkinSection")
        
        self.texture_units.write(f)
        #self.texture_units.fill(f, "M2Batch")
        f.write(struct.pack("I",self.bones))