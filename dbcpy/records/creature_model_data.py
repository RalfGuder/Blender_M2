from dataclasses import make_dataclass
from dbcpy.loc import Loc, NString, Vec3F


_fields = {
    'ID': int,
    'Flags': int,
    'ModelPath': NString,
    'SizeClass': int,
    'modelScale': float,
    'BloodLevel': int,
    'Footprint': int,
    'FootprintTextureLength': float,
    'FootprintTextureWidth': float,
    'FootprintParticleScale': float,
    'FoleyMaterialID': int,
    'FootstepShakeSize': int,
    'DeathThudShakeSize': int,
    'SoundData': int,
    'CollisionWidth': float,
    'CollisionHeight': float,
    'MountHeight': float,
    'GeoBoxMin': Vec3F,
    'GeoBoxMax': Vec3F,
    'WorldEffectScale': float,
    'AttachedEffectScale': float,
    'MissileCollisionRadius' : float,
    'MissileCollisionPush': float,
    'MissileCollisionRaise': float
}

_record = make_dataclass('CreatureModelDataRecord', zip(_fields.keys(), _fields.values()))
_record.field_types = staticmethod(_fields.values())