from dataclasses import make_dataclass
from dbcpy.loc import Loc, NString, Vec3F


_fields = {
    'ID': int,
    'ModelID': int,
    'SoundID': int,
    'ExtraDisplayInformationID': int,
    'Scale': float,
    'Opacity': int,
    'Texture1': NString,
    'Texture2': NString,
    'Texture3': NString,
    'PortraitTextureName': NString,
    'SizeClass': int,
    'BloodID': int,
    'NPCSoundsID': int,
    'ParticlesID': int,
    'CreatureGeosetDataID': int,
    'ObjectEffectPackageID': int
    
}

_record = make_dataclass('CreatureDisplayInfoRec', zip(_fields.keys(), _fields.values()))
_record.field_types = staticmethod(_fields.values())